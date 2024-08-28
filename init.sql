CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS embeddings_nomic_text (
 tenant_id UUID ,
 id UUID DEFAULT gen_random_uuid (),
 file_id UUID,
 embedding  vector(768) NOT NULL,
 primary key (tenant_id, id)
);

CREATE TABLE IF NOT EXISTS embeddings_mxbai_text (
 tenant_id UUID ,
 id UUID DEFAULT gen_random_uuid (),
 file_id UUID,
 embedding  vector(1024) NOT NULL,
 primary key (tenant_id, id)
);

CREATE TABLE IF NOT EXISTS file_content (
tenant_id UUID ,
project_id UUID,
id UUID DEFAULT gen_random_uuid (),
file_name VARCHAR(255) NOT NULL,
contents  TEXT NOT NULL,
primary key (tenant_id, project_id, id)
);

CREATE TABLE IF NOT EXISTS projects (
tenant_id UUID,
id UUID DEFAULT gen_random_uuid (),
name varchar(30),
url varchar(1024),
description TEXT,
primary key (tenant_id, id)
);
