"""Real PostgreSQL + FastAPI + Crust tests. Only run against a migrated rehearsal DB.
TEST_DATABASE=guten_ordering_test_... python -m unittest discover -s tests -v
"""
import concurrent.futures
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import tempfile
import time
import unittest
import uuid
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

ROOT = Path(__file__).resolve().parents[1]


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


class OrderingIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        database = os.environ.get("TEST_DATABASE", "")
        if not database.startswith("guten_") or "_test_" not in database or not database.replace("_", "").isalnum():
            raise RuntimeError("Explicit TEST_DATABASE=guten_*_test_* required; never the master database")
        cls.temp = tempfile.TemporaryDirectory(prefix="guten-order-tests-")
        cls.addClassCleanup(cls.temp.cleanup)
        cls.log = open(Path(cls.temp.name) / "services.log", "w+")
        cls.addClassCleanup(cls.log.close)
        cls.children = []
        cls.addClassCleanup(cls.stop)
        backend_port, gateway_port = free_port(), free_port()
        cls.backend = f"http://127.0.0.1:{backend_port}/guten"
        cls.base = f"http://127.0.0.1:{gateway_port}/api/guten"
        env = dict(os.environ, DATABASE_URL=f"postgresql+asyncpg:///{database}", PYTHONDONTWRITEBYTECODE="1")
        cls.children.append(subprocess.Popen([sys.executable, "-B", "-m", "uvicorn", "app.main:app", "--app-dir", str(ROOT), "--host", "127.0.0.1", "--port", str(backend_port)], cwd=cls.temp.name, env=env, stdout=cls.log, stderr=cls.log, start_new_session=True))
        crust = ROOT.parent / "guten-crust"
        env = dict(os.environ, PORT=str(gateway_port), GUTEN_DATALAKE_URL=f"http://127.0.0.1:{backend_port}")
        cls.children.append(subprocess.Popen([str(crust / "node_modules/.bin/ts-node"), "src/server.ts"], cwd=crust, env=env, stdout=cls.log, stderr=cls.log, start_new_session=True))
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            try:
                with urlopen(cls.base + "/sites", timeout=1) as response:
                    if response.status == 200: return
            except (OSError, URLError):
                time.sleep(.2)
        cls.log.flush(); cls.log.seek(0)
        raise RuntimeError("Test services did not start: " + cls.log.read()[-5000:])

    @classmethod
    def stop(cls):
        for child in cls.children:
            try: os.killpg(child.pid, signal.SIGTERM)
            except ProcessLookupError: pass
        for child in cls.children:
            try: child.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(child.pid, signal.SIGKILL); child.wait()

    def call(self, method, path, body=None, status=200, backend=False):
        request = Request((self.backend if backend else self.base) + path,
                          data=None if body is None else json.dumps(body).encode(),
                          headers={"Content-Type": "application/json"}, method=method)
        try:
            with urlopen(request, timeout=15) as response: code, payload = response.status, response.read()
        except HTTPError as exc: code, payload = exc.code, exc.read()
        self.assertEqual(code, status, payload.decode())
        return json.loads(payload)

    def site(self, name):
        return self.call("POST", "/sites", dict(name=name,title=name,url="",logo="",favicon="",color=""))

    def section(self, site, name):
        return self.call("POST", "/sections", dict(site_name=site,name=name,title=name))

    def page(self, site, section, name):
        return self.call("POST", "/pages", dict(site_name=site,section_name=section,name=name,title=name,content="Original content"))

    def setUp(self):
        self.names = ["test_a_" + uuid.uuid4().hex, "test_b_" + uuid.uuid4().hex]
        self.addCleanup(self.cleanup_sites)
        self.a, self.b = self.names
        self.site(self.a); self.site(self.b)
        self.empty = self.section(self.a, "empty")
        self.sa = self.section(self.a, "shared")
        self.sb = self.section(self.b, "shared")
        self.other = self.section(self.a, "other")
        self.pa = self.page(self.a,"shared","same")
        self.pb = self.page(self.b,"shared","same")
        self.pc = self.page(self.a,"other","same")
        self.second = self.page(self.a,"shared","second")

    def cleanup_sites(self):
        for name in self.names:
            self.call("DELETE", "/sites/" + name)

    def test_scoped_names_and_append(self):
        self.call("POST", "/sections", dict(site_name=self.a,name="shared",title="duplicate"),status=409)
        self.call("POST", "/pages", dict(site_name=self.a,section_name="shared",name="same",title="duplicate"),status=409)
        self.section(self.b,"foreign")
        self.call("POST", "/pages", dict(site_name=self.a,section_name="foreign",name="bad",title="bad"),status=404)
        rows=self.call("GET",f"/pages?site={self.a}&section=shared")
        self.assertEqual([p["id"] for p in rows],[self.pa["id"],self.second["id"]])
        self.assertEqual([p["sort_order"] for p in rows],[0,1])
        self.assertEqual(self.call("GET",f"/pages/same?site={self.b}&section=shared")["id"],self.pb["id"])

    def test_atomic_order_and_stale_requests(self):
        ids=[self.empty["id"],self.sa["id"],self.other["id"]]
        endpoint=f"/sites/{self.a}/sections/order"
        for invalid in [[ids[0],ids[0],ids[2]],[ids[0]],[*ids,self.sb["id"]],[True,ids[1],ids[2]]]:
            self.call("PUT",endpoint,dict(ids=invalid,expected_ids=ids),status=422)
        self.assertEqual([s["id"] for s in self.call("GET",f"/sections?site={self.a}")],ids)
        ordered=self.call("PUT",endpoint,dict(ids=ids[::-1],expected_ids=ids))
        self.assertEqual([s["sort_order"] for s in ordered],[0,1,2])
        self.call("PUT",endpoint,dict(ids=ids,expected_ids=ids),status=409)
        self.assertEqual([s["id"] for s in self.call("GET",f"/sections?site={self.b}")],[self.sb["id"]])
        pages=[self.pa["id"],self.second["id"]]
        self.call("PUT",f"/sites/{self.a}/sections/shared/pages/order",dict(ids=pages[::-1],expected_ids=pages))
        new=self.page(self.a,"shared","last")
        self.assertEqual(new["sort_order"],2)
        self.assertEqual([p["id"] for p in self.call("GET",f"/pages?site={self.a}&section=shared")],pages[::-1]+[new["id"]])

    def test_simultaneous_reorder_conflicts(self):
        ids=[self.pa["id"],self.second["id"]]
        def reorder():
            request=Request(self.base+f"/sites/{self.a}/sections/shared/pages/order", data=json.dumps(dict(ids=ids[::-1],expected_ids=ids)).encode(),headers={"Content-Type":"application/json"},method="PUT")
            try:
                with urlopen(request,timeout=15) as response: return response.status
            except HTTPError as exc: return exc.code
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            self.assertEqual(sorted(pool.map(lambda _: reorder(),range(2))),[200,409])

    def test_landing_validation_and_fallback(self):
        self.assertEqual(self.call("GET",f"/sites/{self.a}/landing"),dict(section_name="shared",page_name="same"))
        self.call("GET",f"/sites/{self.a}/landing?section=empty",status=404)
        body=dict(title=self.a,url="",logo="",favicon="",color="",landing_page_id=self.pb["id"])
        self.call("PUT",f"/sites/{self.a}",body,status=422)
        body["landing_page_id"]=self.pc["id"]
        self.assertEqual(self.call("PUT",f"/sites/{self.a}",body)["landing_page_id"],self.pc["id"])
        self.assertEqual(self.call("GET",f"/sites/{self.a}/landing")["section_name"],"other")
        self.call("DELETE",f'/pages/{self.pc["id"]}')
        self.assertIsNone(self.call("GET",f"/sites/{self.a}")["landing_page_id"])
        self.assertEqual(self.call("GET",f"/sites/{self.a}/landing")["section_name"],"shared")

    def test_rename_preserves_identity_and_order(self):
        body=dict(site_name=self.a,section_name="shared",name="renamed",title="Renamed",content="Updated",primary_image="/assets/example.png")
        result=self.call("PUT",f'/page_by_id/{self.pa["id"]}',body,backend=True)
        self.assertEqual((result["id"],result["sort_order"]),(self.pa["id"],0))
        self.assertEqual(result["primary_image"],"/assets/example.png")
        result=self.call("PUT",f'/sections/{self.sa["id"]}',dict(name="renamed-section",title="Renamed",label="R"))
        self.assertEqual(result["sort_order"],1)
        self.assertEqual(self.call("GET",f"/pages/renamed?site={self.a}&section=renamed-section")["id"],self.pa["id"])
        rows=self.call("GET",f"/pages_all/{self.a}")
        self.assertTrue(all(row["section_name"] for row in rows))

    def test_editorial_crud_and_scope(self):
        scope = dict(site_name=self.a, section_name="shared", page_name="same")
        query = f"?site={self.a}&section=shared&page=same"
        foreign_query = f"?site={self.b}&section=shared&page=same"
        other_query = f"?site={self.a}&section=other&page=same"
        for kind, fields, updated in [
            ("refs", dict(url="https://example.com/a", description="Original"), dict(url="http://example.com/b", description="Updated")),
            ("notes", dict(note="**Original**\n\nNote"), dict(note="  **Updated**\n\nNote  ")),
        ]:
            with self.subTest(kind=kind):
                self.assertEqual(self.call("GET", f"/{kind}"+query), [])
                item = self.call("POST", f"/{kind}", {**scope, **fields})
                item2 = self.call("POST", f"/{kind}", {**scope, **fields})
                self.assertEqual(item["page_id"], self.pa["id"])
                self.assertEqual([row["id"] for row in self.call("GET", f"/{kind}"+query)], [item["id"], item2["id"]])
                self.assertEqual(self.call("GET", f"/{kind}"+foreign_query), [])
                endpoint=f'/{kind}/{item["id"]}'
                for wrong in [dict(site_name=self.b), dict(section_name="other"), dict(page_name="second")]:
                    self.call("PUT", endpoint, {**scope, **updated, **wrong}, status=404)
                for wrong in [foreign_query, other_query]:
                    self.call("DELETE", endpoint+wrong, status=404)
                self.call("DELETE", endpoint, status=422)
                before=self.call("GET", f"/{kind}"+query)[0]
                for key,value in fields.items(): self.assertEqual(before[key],value)
                saved=self.call("PUT", endpoint, {**scope, **updated})
                self.assertEqual(saved["id"], item["id"])
                self.assertEqual(saved["page_id"], self.pa["id"])
                for key,value in updated.items(): self.assertEqual(saved[key],value)
                self.call("DELETE", endpoint+query)
                self.call("DELETE", endpoint+query, status=404)
                self.call("PUT", endpoint, {**scope, **updated}, status=404)
                self.assertEqual([row["id"] for row in self.call("GET", f"/{kind}"+query)], [item2["id"]])

    def test_editorial_validation_and_missing_parents(self):
        scope=dict(site_name=self.a,section_name="shared",page_name="same")
        query=f"?site={self.a}&section=shared&page=same"
        ref=self.call("POST", "/refs", {**scope,"url":"  https://example.com  "})
        self.assertEqual(ref["url"],"https://example.com")
        self.assertIsNone(ref["description"])
        note=self.call("POST", "/notes", {**scope,"note":"Keep me"})
        for bad in ["", "javascript:alert(1)", "data:text/html,hello", "ftp://example.com", "/relative", "https://example.com/"+"a"*256]:
            self.call("POST", "/refs", {**scope,"url":bad},status=422)
            self.call("PUT", f'/refs/{ref["id"]}', {**scope,"url":bad},status=422)
        for bad in ["", "  \n\t", None]:
            self.call("POST", "/notes", {**scope,"note":bad},status=422)
            self.call("PUT", f'/notes/{note["id"]}', {**scope,"note":bad},status=422)
        for kind,fields in [("refs",dict(url="https://example.com")),("notes",dict(note="Text"))]:
            self.call("POST",f"/{kind}",{**scope,**fields,"page_name":"missing"},status=404)
            self.call("GET",f"/{kind}?site={self.a}&section=shared&page=missing",status=404)
            self.call("POST",f"/{kind}",fields,status=422)
            self.call("GET",f"/{kind}",status=422)
            self.call("DELETE",f"/{kind}/invalid"+query,status=422)
            self.assertEqual(len(self.call("GET",f"/{kind}"+query)),1)
        self.assertEqual(self.call("GET","/notes"+query)[0]["note"],"Keep me")

    def test_editorial_rename_and_page_deletion(self):
        scope=dict(site_name=self.a,section_name="shared",page_name="same")
        self.call("POST","/refs",{**scope,"url":"https://example.com"})
        self.call("POST","/notes",{**scope,"note":"Note retained through rename"})
        self.call("PUT","/pages/same",dict(site_name=self.a,section_name="shared",name="renamed",title="Renamed",content="Content"))
        for kind in ["refs","notes"]:
            self.call("GET",f"/{kind}?site={self.a}&section=shared&page=same",status=404)
            self.assertEqual(len(self.call("GET",f"/{kind}?site={self.a}&section=shared&page=renamed")),1)
        self.call("DELETE",f'/pages/{self.pa["id"]}')
        self.page(self.a,"shared","renamed")
        for kind in ["refs","notes"]:
            self.assertEqual(self.call("GET",f"/{kind}?site={self.a}&section=shared&page=renamed"),[])


if __name__ == "__main__":
    unittest.main()
