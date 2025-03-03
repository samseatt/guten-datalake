-- 1️ Create Database (Skip if already exists)
-- CREATE DATABASE guten_datalake;
-- \c guten_datalake

-- 2️ Create Schemas
CREATE SCHEMA IF NOT EXISTS draft;
CREATE SCHEMA IF NOT EXISTS published;
CREATE SCHEMA IF NOT EXISTS workflow;

-- 3️ Draft Schema (For Editing & Staging)

-- Themes Table (Created first to be referenced later)
CREATE TABLE IF NOT EXISTS draft.themes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    primary_color VARCHAR(7),    
    background_color VARCHAR(7), 
    created_at TIMESTAMP DEFAULT NOW()
);

-- Sites Table
CREATE TABLE IF NOT EXISTS draft.sites (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,  
    title VARCHAR(255) NOT NULL,        
    logo VARCHAR(255),                  
    url VARCHAR(255),                    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Sections Table
CREATE TABLE IF NOT EXISTS draft.sections (
    id SERIAL PRIMARY KEY,
    site_id INT REFERENCES draft.sites(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,      
    theme_id INT REFERENCES draft.themes(id),  
    sort_order INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Templates Table
CREATE TABLE IF NOT EXISTS draft.templates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    layout_options JSONB NOT NULL, 
    created_at TIMESTAMP DEFAULT NOW()
);

-- Pages Table
CREATE TABLE IF NOT EXISTS draft.pages (
    id SERIAL PRIMARY KEY,
    section_id INT REFERENCES draft.sections(id) ON DELETE CASCADE,
    template_id INT REFERENCES draft.templates(id),  
    name VARCHAR(255) NOT NULL UNIQUE,         
    primary_image VARCHAR(255),                     
    abstract TEXT,                                  
    content TEXT NOT NULL,                          
    tags TEXT[],                                    
    sort_order INT DEFAULT 0,                       
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Refs Table
CREATE TABLE IF NOT EXISTS draft.refs (
    id SERIAL PRIMARY KEY,
    page_id INT REFERENCES draft.pages(id) ON DELETE CASCADE,
    url VARCHAR(255) NOT NULL,
    description TEXT,
    type VARCHAR(50) CHECK (type IN ('white_paper', 'external_link')),
    sort_order INT DEFAULT 0
);

-- Notes Table
CREATE TABLE IF NOT EXISTS draft.notes (
    id SERIAL PRIMARY KEY,
    page_id INT REFERENCES draft.pages(id) ON DELETE CASCADE,
    note TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Users Table
CREATE TABLE IF NOT EXISTS draft.users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role VARCHAR(50) CHECK (role IN ('admin', 'editor', 'viewer')),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 4️ Published Schema (Publicly Accessible) **FIXED**

-- Explicitly Define Published Tables and Primary Keys
CREATE TABLE IF NOT EXISTS published.sites (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,  
    title VARCHAR(255) NOT NULL,        
    logo VARCHAR(255),                  
    url VARCHAR(255),                    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS published.sections (
    id SERIAL PRIMARY KEY,
    site_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,      
    theme_id INT,
    sort_order INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT fk_published_site FOREIGN KEY (site_id) REFERENCES published.sites(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS published.templates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    layout_options JSONB NOT NULL, 
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS published.pages (
    id SERIAL PRIMARY KEY,
    section_id INT NOT NULL,
    template_id INT,
    name VARCHAR(255) NOT NULL UNIQUE,         
    primary_image VARCHAR(255),                     
    abstract TEXT,                                  
    content TEXT NOT NULL,                          
    tags TEXT[],                                    
    sort_order INT DEFAULT 0,                       
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT fk_published_section FOREIGN KEY (section_id) REFERENCES published.sections(id) ON DELETE CASCADE,
    CONSTRAINT fk_published_template FOREIGN KEY (template_id) REFERENCES published.templates(id)
);

CREATE TABLE IF NOT EXISTS published.refs (
    id SERIAL PRIMARY KEY,
    page_id INT NOT NULL,
    url VARCHAR(255) NOT NULL,
    description TEXT,
    type VARCHAR(50) CHECK (type IN ('white_paper', 'external_link')),
    sort_order INT DEFAULT 0,
    CONSTRAINT fk_published_page FOREIGN KEY (page_id) REFERENCES published.pages(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS published.notes (
    id SERIAL PRIMARY KEY,
    page_id INT NOT NULL,
    note TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT fk_published_page FOREIGN KEY (page_id) REFERENCES published.pages(id) ON DELETE CASCADE
);

-- 5️ Workflow Schema (Publishing Lifecycle & AI Processing)

-- Tracks publishing requests & approvals
CREATE TABLE IF NOT EXISTS workflow.publishing_requests (
    id SERIAL PRIMARY KEY,
    site_id INT REFERENCES draft.sites(id) ON DELETE CASCADE,
    requested_by INT REFERENCES draft.users(id),
    status VARCHAR(50) CHECK (status IN ('pending', 'approved', 'rejected')) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW(),
    reviewed_by INT REFERENCES draft.users(id),
    reviewed_at TIMESTAMP
);

-- Tracks AI-generated content updates
CREATE TABLE IF NOT EXISTS workflow.llm_updates (
    id SERIAL PRIMARY KEY,
    page_id INT REFERENCES draft.pages(id) ON DELETE CASCADE,
    updated_content TEXT NOT NULL,  
    ai_model_used VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tracks publishing history (Audit Log)
CREATE TABLE IF NOT EXISTS workflow.publishing_log (
    id SERIAL PRIMARY KEY,
    site_id INT REFERENCES draft.sites(id) ON DELETE CASCADE,
    action VARCHAR(50) CHECK (action IN ('publish', 'rollback', 'update')),
    performed_by INT REFERENCES draft.users(id),
    timestamp TIMESTAMP DEFAULT NOW(),
    details TEXT
);
