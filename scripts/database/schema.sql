-- Baseline captured from the live Guten schema, 2026-09-17.
-- For a NEW empty database only; then run migrate.py. Never rerun on existing data.
--
-- PostgreSQL database dump
--

-- Dumped from database version 14.13 (Homebrew)
-- Dumped by pg_dump version 14.13 (Homebrew)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: draft; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA draft;


--
-- Name: published; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA published;


--
-- Name: workflow; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA workflow;


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: notes; Type: TABLE; Schema: draft; Owner: -
--

CREATE TABLE draft.notes (
    id integer NOT NULL,
    page_id integer,
    note text NOT NULL,
    created_at timestamp without time zone DEFAULT now()
);


--
-- Name: notes_id_seq; Type: SEQUENCE; Schema: draft; Owner: -
--

CREATE SEQUENCE draft.notes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: notes_id_seq; Type: SEQUENCE OWNED BY; Schema: draft; Owner: -
--

ALTER SEQUENCE draft.notes_id_seq OWNED BY draft.notes.id;


--
-- Name: pages; Type: TABLE; Schema: draft; Owner: -
--

CREATE TABLE draft.pages (
    id integer NOT NULL,
    section_id integer,
    template_id integer,
    name character varying(255) NOT NULL,
    primary_image character varying(255),
    abstract text,
    content text NOT NULL,
    tags text[],
    sort_order integer DEFAULT 0,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now(),
    title text
);


--
-- Name: pages_id_seq; Type: SEQUENCE; Schema: draft; Owner: -
--

CREATE SEQUENCE draft.pages_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: pages_id_seq; Type: SEQUENCE OWNED BY; Schema: draft; Owner: -
--

ALTER SEQUENCE draft.pages_id_seq OWNED BY draft.pages.id;


--
-- Name: refs; Type: TABLE; Schema: draft; Owner: -
--

CREATE TABLE draft.refs (
    id integer NOT NULL,
    page_id integer,
    url character varying(255) NOT NULL,
    description text,
    type character varying(50),
    sort_order integer DEFAULT 0,
    CONSTRAINT refs_type_check CHECK (((type)::text = ANY (ARRAY[('white_paper'::character varying)::text, ('external_link'::character varying)::text])))
);


--
-- Name: refs_id_seq; Type: SEQUENCE; Schema: draft; Owner: -
--

CREATE SEQUENCE draft.refs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: refs_id_seq; Type: SEQUENCE OWNED BY; Schema: draft; Owner: -
--

ALTER SEQUENCE draft.refs_id_seq OWNED BY draft.refs.id;


--
-- Name: sections; Type: TABLE; Schema: draft; Owner: -
--

CREATE TABLE draft.sections (
    id integer NOT NULL,
    site_id integer,
    name character varying(255) NOT NULL,
    section_theme_id integer,
    sort_order integer DEFAULT 0,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now(),
    title text,
    label text
);


--
-- Name: sections_id_seq; Type: SEQUENCE; Schema: draft; Owner: -
--

CREATE SEQUENCE draft.sections_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: sections_id_seq; Type: SEQUENCE OWNED BY; Schema: draft; Owner: -
--

ALTER SEQUENCE draft.sections_id_seq OWNED BY draft.sections.id;


--
-- Name: sites; Type: TABLE; Schema: draft; Owner: -
--

CREATE TABLE draft.sites (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    title character varying(255) NOT NULL,
    logo character varying(255),
    url character varying(255),
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now(),
    landing_page_id integer,
    favicon text,
    color text
);


--
-- Name: sites_id_seq; Type: SEQUENCE; Schema: draft; Owner: -
--

CREATE SEQUENCE draft.sites_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: sites_id_seq; Type: SEQUENCE OWNED BY; Schema: draft; Owner: -
--

ALTER SEQUENCE draft.sites_id_seq OWNED BY draft.sites.id;


--
-- Name: templates; Type: TABLE; Schema: draft; Owner: -
--

CREATE TABLE draft.templates (
    id integer NOT NULL,
    template_name character varying(255) NOT NULL,
    layout_options jsonb NOT NULL,
    created_at timestamp without time zone DEFAULT now()
);


--
-- Name: templates_id_seq; Type: SEQUENCE; Schema: draft; Owner: -
--

CREATE SEQUENCE draft.templates_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: templates_id_seq; Type: SEQUENCE OWNED BY; Schema: draft; Owner: -
--

ALTER SEQUENCE draft.templates_id_seq OWNED BY draft.templates.id;


--
-- Name: themes; Type: TABLE; Schema: draft; Owner: -
--

CREATE TABLE draft.themes (
    id integer NOT NULL,
    theme_name character varying(255) NOT NULL,
    primary_color character varying(7),
    background_color character varying(7),
    created_at timestamp without time zone DEFAULT now()
);


--
-- Name: themes_id_seq; Type: SEQUENCE; Schema: draft; Owner: -
--

CREATE SEQUENCE draft.themes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: themes_id_seq; Type: SEQUENCE OWNED BY; Schema: draft; Owner: -
--

ALTER SEQUENCE draft.themes_id_seq OWNED BY draft.themes.id;


--
-- Name: users; Type: TABLE; Schema: draft; Owner: -
--

CREATE TABLE draft.users (
    id integer NOT NULL,
    email character varying(255) NOT NULL,
    password_hash text NOT NULL,
    role character varying(50),
    created_at timestamp without time zone DEFAULT now(),
    CONSTRAINT users_role_check CHECK (((role)::text = ANY (ARRAY[('admin'::character varying)::text, ('editor'::character varying)::text, ('viewer'::character varying)::text])))
);


--
-- Name: users_id_seq; Type: SEQUENCE; Schema: draft; Owner: -
--

CREATE SEQUENCE draft.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: draft; Owner: -
--

ALTER SEQUENCE draft.users_id_seq OWNED BY draft.users.id;


--
-- Name: notes; Type: TABLE; Schema: published; Owner: -
--

CREATE TABLE published.notes (
    id integer NOT NULL,
    page_id integer NOT NULL,
    note text NOT NULL,
    created_at timestamp without time zone DEFAULT now()
);


--
-- Name: notes_id_seq; Type: SEQUENCE; Schema: published; Owner: -
--

CREATE SEQUENCE published.notes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: notes_id_seq; Type: SEQUENCE OWNED BY; Schema: published; Owner: -
--

ALTER SEQUENCE published.notes_id_seq OWNED BY published.notes.id;


--
-- Name: pages; Type: TABLE; Schema: published; Owner: -
--

CREATE TABLE published.pages (
    id integer NOT NULL,
    section_id integer NOT NULL,
    template_id integer,
    page_name character varying(255) NOT NULL,
    primary_image character varying(255),
    abstract text,
    content text NOT NULL,
    tags text[],
    sort_order integer DEFAULT 0,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now()
);


--
-- Name: pages_id_seq; Type: SEQUENCE; Schema: published; Owner: -
--

CREATE SEQUENCE published.pages_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: pages_id_seq; Type: SEQUENCE OWNED BY; Schema: published; Owner: -
--

ALTER SEQUENCE published.pages_id_seq OWNED BY published.pages.id;


--
-- Name: refs; Type: TABLE; Schema: published; Owner: -
--

CREATE TABLE published.refs (
    id integer NOT NULL,
    page_id integer NOT NULL,
    url character varying(255) NOT NULL,
    description text,
    type character varying(50),
    sort_order integer DEFAULT 0,
    CONSTRAINT refs_type_check CHECK (((type)::text = ANY (ARRAY[('white_paper'::character varying)::text, ('external_link'::character varying)::text])))
);


--
-- Name: refs_id_seq; Type: SEQUENCE; Schema: published; Owner: -
--

CREATE SEQUENCE published.refs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: refs_id_seq; Type: SEQUENCE OWNED BY; Schema: published; Owner: -
--

ALTER SEQUENCE published.refs_id_seq OWNED BY published.refs.id;


--
-- Name: sections; Type: TABLE; Schema: published; Owner: -
--

CREATE TABLE published.sections (
    id integer NOT NULL,
    site_id integer NOT NULL,
    section_name character varying(255) NOT NULL,
    section_theme_id integer,
    sort_order integer DEFAULT 0,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now()
);


--
-- Name: sections_id_seq; Type: SEQUENCE; Schema: published; Owner: -
--

CREATE SEQUENCE published.sections_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: sections_id_seq; Type: SEQUENCE OWNED BY; Schema: published; Owner: -
--

ALTER SEQUENCE published.sections_id_seq OWNED BY published.sections.id;


--
-- Name: sites; Type: TABLE; Schema: published; Owner: -
--

CREATE TABLE published.sites (
    id integer NOT NULL,
    site_name character varying(255) NOT NULL,
    site_title character varying(255) NOT NULL,
    site_logo character varying(255),
    site_url character varying(255),
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now()
);


--
-- Name: sites_id_seq; Type: SEQUENCE; Schema: published; Owner: -
--

CREATE SEQUENCE published.sites_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: sites_id_seq; Type: SEQUENCE OWNED BY; Schema: published; Owner: -
--

ALTER SEQUENCE published.sites_id_seq OWNED BY published.sites.id;


--
-- Name: templates; Type: TABLE; Schema: published; Owner: -
--

CREATE TABLE published.templates (
    id integer NOT NULL,
    template_name character varying(255) NOT NULL,
    layout_options jsonb NOT NULL,
    created_at timestamp without time zone DEFAULT now()
);


--
-- Name: templates_id_seq; Type: SEQUENCE; Schema: published; Owner: -
--

CREATE SEQUENCE published.templates_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: templates_id_seq; Type: SEQUENCE OWNED BY; Schema: published; Owner: -
--

ALTER SEQUENCE published.templates_id_seq OWNED BY published.templates.id;


--
-- Name: llm_updates; Type: TABLE; Schema: workflow; Owner: -
--

CREATE TABLE workflow.llm_updates (
    id integer NOT NULL,
    page_id integer,
    updated_content text NOT NULL,
    ai_model_used character varying(255),
    created_at timestamp without time zone DEFAULT now()
);


--
-- Name: llm_updates_id_seq; Type: SEQUENCE; Schema: workflow; Owner: -
--

CREATE SEQUENCE workflow.llm_updates_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: llm_updates_id_seq; Type: SEQUENCE OWNED BY; Schema: workflow; Owner: -
--

ALTER SEQUENCE workflow.llm_updates_id_seq OWNED BY workflow.llm_updates.id;


--
-- Name: publishing_log; Type: TABLE; Schema: workflow; Owner: -
--

CREATE TABLE workflow.publishing_log (
    id integer NOT NULL,
    site_id integer,
    action character varying(50),
    performed_by integer,
    "timestamp" timestamp without time zone DEFAULT now(),
    details text,
    CONSTRAINT publishing_log_action_check CHECK (((action)::text = ANY (ARRAY[('publish'::character varying)::text, ('rollback'::character varying)::text, ('update'::character varying)::text])))
);


--
-- Name: publishing_log_id_seq; Type: SEQUENCE; Schema: workflow; Owner: -
--

CREATE SEQUENCE workflow.publishing_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: publishing_log_id_seq; Type: SEQUENCE OWNED BY; Schema: workflow; Owner: -
--

ALTER SEQUENCE workflow.publishing_log_id_seq OWNED BY workflow.publishing_log.id;


--
-- Name: publishing_requests; Type: TABLE; Schema: workflow; Owner: -
--

CREATE TABLE workflow.publishing_requests (
    id integer NOT NULL,
    site_id integer,
    requested_by integer,
    status character varying(50) DEFAULT 'pending'::character varying,
    created_at timestamp without time zone DEFAULT now(),
    reviewed_by integer,
    reviewed_at timestamp without time zone,
    CONSTRAINT publishing_requests_status_check CHECK (((status)::text = ANY (ARRAY[('pending'::character varying)::text, ('approved'::character varying)::text, ('rejected'::character varying)::text])))
);


--
-- Name: publishing_requests_id_seq; Type: SEQUENCE; Schema: workflow; Owner: -
--

CREATE SEQUENCE workflow.publishing_requests_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: publishing_requests_id_seq; Type: SEQUENCE OWNED BY; Schema: workflow; Owner: -
--

ALTER SEQUENCE workflow.publishing_requests_id_seq OWNED BY workflow.publishing_requests.id;


--
-- Name: notes id; Type: DEFAULT; Schema: draft; Owner: -
--

ALTER TABLE ONLY draft.notes ALTER COLUMN id SET DEFAULT nextval('draft.notes_id_seq'::regclass);


--
-- Name: pages id; Type: DEFAULT; Schema: draft; Owner: -
--

ALTER TABLE ONLY draft.pages ALTER COLUMN id SET DEFAULT nextval('draft.pages_id_seq'::regclass);


--
-- Name: refs id; Type: DEFAULT; Schema: draft; Owner: -
--

ALTER TABLE ONLY draft.refs ALTER COLUMN id SET DEFAULT nextval('draft.refs_id_seq'::regclass);


--
-- Name: sections id; Type: DEFAULT; Schema: draft; Owner: -
--

ALTER TABLE ONLY draft.sections ALTER COLUMN id SET DEFAULT nextval('draft.sections_id_seq'::regclass);


--
-- Name: sites id; Type: DEFAULT; Schema: draft; Owner: -
--

ALTER TABLE ONLY draft.sites ALTER COLUMN id SET DEFAULT nextval('draft.sites_id_seq'::regclass);


--
-- Name: templates id; Type: DEFAULT; Schema: draft; Owner: -
--

ALTER TABLE ONLY draft.templates ALTER COLUMN id SET DEFAULT nextval('draft.templates_id_seq'::regclass);


--
-- Name: themes id; Type: DEFAULT; Schema: draft; Owner: -
--

ALTER TABLE ONLY draft.themes ALTER COLUMN id SET DEFAULT nextval('draft.themes_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: draft; Owner: -
--

ALTER TABLE ONLY draft.users ALTER COLUMN id SET DEFAULT nextval('draft.users_id_seq'::regclass);


--
-- Name: notes id; Type: DEFAULT; Schema: published; Owner: -
--

ALTER TABLE ONLY published.notes ALTER COLUMN id SET DEFAULT nextval('published.notes_id_seq'::regclass);


--
-- Name: pages id; Type: DEFAULT; Schema: published; Owner: -
--

ALTER TABLE ONLY published.pages ALTER COLUMN id SET DEFAULT nextval('published.pages_id_seq'::regclass);


--
-- Name: refs id; Type: DEFAULT; Schema: published; Owner: -
--

ALTER TABLE ONLY published.refs ALTER COLUMN id SET DEFAULT nextval('published.refs_id_seq'::regclass);


--
-- Name: sections id; Type: DEFAULT; Schema: published; Owner: -
--

ALTER TABLE ONLY published.sections ALTER COLUMN id SET DEFAULT nextval('published.sections_id_seq'::regclass);


--
-- Name: sites id; Type: DEFAULT; Schema: published; Owner: -
--

ALTER TABLE ONLY published.sites ALTER COLUMN id SET DEFAULT nextval('published.sites_id_seq'::regclass);


--
-- Name: templates id; Type: DEFAULT; Schema: published; Owner: -
--

ALTER TABLE ONLY published.templates ALTER COLUMN id SET DEFAULT nextval('published.templates_id_seq'::regclass);


--
-- Name: llm_updates id; Type: DEFAULT; Schema: workflow; Owner: -
--

ALTER TABLE ONLY workflow.llm_updates ALTER COLUMN id SET DEFAULT nextval('workflow.llm_updates_id_seq'::regclass);


--
-- Name: publishing_log id; Type: DEFAULT; Schema: workflow; Owner: -
--

ALTER TABLE ONLY workflow.publishing_log ALTER COLUMN id SET DEFAULT nextval('workflow.publishing_log_id_seq'::regclass);


--
-- Name: publishing_requests id; Type: DEFAULT; Schema: workflow; Owner: -
--

ALTER TABLE ONLY workflow.publishing_requests ALTER COLUMN id SET DEFAULT nextval('workflow.publishing_requests_id_seq'::regclass);


--
-- Name: notes notes_pkey; Type: CONSTRAINT; Schema: draft; Owner: -
--

ALTER TABLE ONLY draft.notes
    ADD CONSTRAINT notes_pkey PRIMARY KEY (id);


--
-- Name: pages pages_page_name_key; Type: CONSTRAINT; Schema: draft; Owner: -
--

ALTER TABLE ONLY draft.pages
    ADD CONSTRAINT pages_page_name_key UNIQUE (name);


--
-- Name: pages pages_pkey; Type: CONSTRAINT; Schema: draft; Owner: -
--

ALTER TABLE ONLY draft.pages
    ADD CONSTRAINT pages_pkey PRIMARY KEY (id);


--
-- Name: refs refs_pkey; Type: CONSTRAINT; Schema: draft; Owner: -
--

ALTER TABLE ONLY draft.refs
    ADD CONSTRAINT refs_pkey PRIMARY KEY (id);


--
-- Name: sections sections_pkey; Type: CONSTRAINT; Schema: draft; Owner: -
--

ALTER TABLE ONLY draft.sections
    ADD CONSTRAINT sections_pkey PRIMARY KEY (id);


--
-- Name: sites sites_pkey; Type: CONSTRAINT; Schema: draft; Owner: -
--

ALTER TABLE ONLY draft.sites
    ADD CONSTRAINT sites_pkey PRIMARY KEY (id);


--
-- Name: sites sites_site_name_key; Type: CONSTRAINT; Schema: draft; Owner: -
--

ALTER TABLE ONLY draft.sites
    ADD CONSTRAINT sites_site_name_key UNIQUE (name);


--
-- Name: templates templates_pkey; Type: CONSTRAINT; Schema: draft; Owner: -
--

ALTER TABLE ONLY draft.templates
    ADD CONSTRAINT templates_pkey PRIMARY KEY (id);


--
-- Name: themes themes_pkey; Type: CONSTRAINT; Schema: draft; Owner: -
--

ALTER TABLE ONLY draft.themes
    ADD CONSTRAINT themes_pkey PRIMARY KEY (id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: draft; Owner: -
--

ALTER TABLE ONLY draft.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: draft; Owner: -
--

ALTER TABLE ONLY draft.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: notes notes_pkey; Type: CONSTRAINT; Schema: published; Owner: -
--

ALTER TABLE ONLY published.notes
    ADD CONSTRAINT notes_pkey PRIMARY KEY (id);


--
-- Name: pages pages_page_name_key; Type: CONSTRAINT; Schema: published; Owner: -
--

ALTER TABLE ONLY published.pages
    ADD CONSTRAINT pages_page_name_key UNIQUE (page_name);


--
-- Name: pages pages_pkey; Type: CONSTRAINT; Schema: published; Owner: -
--

ALTER TABLE ONLY published.pages
    ADD CONSTRAINT pages_pkey PRIMARY KEY (id);


--
-- Name: refs refs_pkey; Type: CONSTRAINT; Schema: published; Owner: -
--

ALTER TABLE ONLY published.refs
    ADD CONSTRAINT refs_pkey PRIMARY KEY (id);


--
-- Name: sections sections_pkey; Type: CONSTRAINT; Schema: published; Owner: -
--

ALTER TABLE ONLY published.sections
    ADD CONSTRAINT sections_pkey PRIMARY KEY (id);


--
-- Name: sites sites_pkey; Type: CONSTRAINT; Schema: published; Owner: -
--

ALTER TABLE ONLY published.sites
    ADD CONSTRAINT sites_pkey PRIMARY KEY (id);


--
-- Name: sites sites_site_name_key; Type: CONSTRAINT; Schema: published; Owner: -
--

ALTER TABLE ONLY published.sites
    ADD CONSTRAINT sites_site_name_key UNIQUE (site_name);


--
-- Name: templates templates_pkey; Type: CONSTRAINT; Schema: published; Owner: -
--

ALTER TABLE ONLY published.templates
    ADD CONSTRAINT templates_pkey PRIMARY KEY (id);


--
-- Name: llm_updates llm_updates_pkey; Type: CONSTRAINT; Schema: workflow; Owner: -
--

ALTER TABLE ONLY workflow.llm_updates
    ADD CONSTRAINT llm_updates_pkey PRIMARY KEY (id);


--
-- Name: publishing_log publishing_log_pkey; Type: CONSTRAINT; Schema: workflow; Owner: -
--

ALTER TABLE ONLY workflow.publishing_log
    ADD CONSTRAINT publishing_log_pkey PRIMARY KEY (id);


--
-- Name: publishing_requests publishing_requests_pkey; Type: CONSTRAINT; Schema: workflow; Owner: -
--

ALTER TABLE ONLY workflow.publishing_requests
    ADD CONSTRAINT publishing_requests_pkey PRIMARY KEY (id);


--
-- Name: notes notes_page_id_fkey; Type: FK CONSTRAINT; Schema: draft; Owner: -
--

ALTER TABLE ONLY draft.notes
    ADD CONSTRAINT notes_page_id_fkey FOREIGN KEY (page_id) REFERENCES draft.pages(id) ON DELETE CASCADE;


--
-- Name: pages pages_section_id_fkey; Type: FK CONSTRAINT; Schema: draft; Owner: -
--

ALTER TABLE ONLY draft.pages
    ADD CONSTRAINT pages_section_id_fkey FOREIGN KEY (section_id) REFERENCES draft.sections(id) ON DELETE CASCADE;


--
-- Name: pages pages_template_id_fkey; Type: FK CONSTRAINT; Schema: draft; Owner: -
--

ALTER TABLE ONLY draft.pages
    ADD CONSTRAINT pages_template_id_fkey FOREIGN KEY (template_id) REFERENCES draft.templates(id);


--
-- Name: refs refs_page_id_fkey; Type: FK CONSTRAINT; Schema: draft; Owner: -
--

ALTER TABLE ONLY draft.refs
    ADD CONSTRAINT refs_page_id_fkey FOREIGN KEY (page_id) REFERENCES draft.pages(id) ON DELETE CASCADE;


--
-- Name: sections sections_section_theme_id_fkey; Type: FK CONSTRAINT; Schema: draft; Owner: -
--

ALTER TABLE ONLY draft.sections
    ADD CONSTRAINT sections_section_theme_id_fkey FOREIGN KEY (section_theme_id) REFERENCES draft.themes(id);


--
-- Name: sections sections_site_id_fkey; Type: FK CONSTRAINT; Schema: draft; Owner: -
--

ALTER TABLE ONLY draft.sections
    ADD CONSTRAINT sections_site_id_fkey FOREIGN KEY (site_id) REFERENCES draft.sites(id) ON DELETE CASCADE;


--
-- Name: sites sites_landing_page_id_fkey; Type: FK CONSTRAINT; Schema: draft; Owner: -
--

ALTER TABLE ONLY draft.sites
    ADD CONSTRAINT sites_landing_page_id_fkey FOREIGN KEY (landing_page_id) REFERENCES draft.pages(id) ON DELETE SET NULL;


--
-- Name: refs fk_published_page; Type: FK CONSTRAINT; Schema: published; Owner: -
--

ALTER TABLE ONLY published.refs
    ADD CONSTRAINT fk_published_page FOREIGN KEY (page_id) REFERENCES published.pages(id) ON DELETE CASCADE;


--
-- Name: notes fk_published_page; Type: FK CONSTRAINT; Schema: published; Owner: -
--

ALTER TABLE ONLY published.notes
    ADD CONSTRAINT fk_published_page FOREIGN KEY (page_id) REFERENCES published.pages(id) ON DELETE CASCADE;


--
-- Name: pages fk_published_section; Type: FK CONSTRAINT; Schema: published; Owner: -
--

ALTER TABLE ONLY published.pages
    ADD CONSTRAINT fk_published_section FOREIGN KEY (section_id) REFERENCES published.sections(id) ON DELETE CASCADE;


--
-- Name: sections fk_published_site; Type: FK CONSTRAINT; Schema: published; Owner: -
--

ALTER TABLE ONLY published.sections
    ADD CONSTRAINT fk_published_site FOREIGN KEY (site_id) REFERENCES published.sites(id) ON DELETE CASCADE;


--
-- Name: pages fk_published_template; Type: FK CONSTRAINT; Schema: published; Owner: -
--

ALTER TABLE ONLY published.pages
    ADD CONSTRAINT fk_published_template FOREIGN KEY (template_id) REFERENCES published.templates(id);


--
-- Name: llm_updates llm_updates_page_id_fkey; Type: FK CONSTRAINT; Schema: workflow; Owner: -
--

ALTER TABLE ONLY workflow.llm_updates
    ADD CONSTRAINT llm_updates_page_id_fkey FOREIGN KEY (page_id) REFERENCES draft.pages(id) ON DELETE CASCADE;


--
-- Name: publishing_log publishing_log_performed_by_fkey; Type: FK CONSTRAINT; Schema: workflow; Owner: -
--

ALTER TABLE ONLY workflow.publishing_log
    ADD CONSTRAINT publishing_log_performed_by_fkey FOREIGN KEY (performed_by) REFERENCES draft.users(id);


--
-- Name: publishing_log publishing_log_site_id_fkey; Type: FK CONSTRAINT; Schema: workflow; Owner: -
--

ALTER TABLE ONLY workflow.publishing_log
    ADD CONSTRAINT publishing_log_site_id_fkey FOREIGN KEY (site_id) REFERENCES draft.sites(id) ON DELETE CASCADE;


--
-- Name: publishing_requests publishing_requests_requested_by_fkey; Type: FK CONSTRAINT; Schema: workflow; Owner: -
--

ALTER TABLE ONLY workflow.publishing_requests
    ADD CONSTRAINT publishing_requests_requested_by_fkey FOREIGN KEY (requested_by) REFERENCES draft.users(id);


--
-- Name: publishing_requests publishing_requests_reviewed_by_fkey; Type: FK CONSTRAINT; Schema: workflow; Owner: -
--

ALTER TABLE ONLY workflow.publishing_requests
    ADD CONSTRAINT publishing_requests_reviewed_by_fkey FOREIGN KEY (reviewed_by) REFERENCES draft.users(id);


--
-- Name: publishing_requests publishing_requests_site_id_fkey; Type: FK CONSTRAINT; Schema: workflow; Owner: -
--

ALTER TABLE ONLY workflow.publishing_requests
    ADD CONSTRAINT publishing_requests_site_id_fkey FOREIGN KEY (site_id) REFERENCES draft.sites(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--
