--
-- PostgreSQL database dump
--

-- Dumped from database version 14.5 (Ubuntu 14.5-0ubuntu0.22.04.1)
-- Dumped by pg_dump version 14.5 (Ubuntu 14.5-0ubuntu0.22.04.1)

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: clients; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.clients (
    name text NOT NULL,
    password text NOT NULL,
    is_online double precision,
    public_key text
);


ALTER TABLE public.clients OWNER TO postgres;

--
-- Name: grp_modified; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.grp_modified (
    grpname text NOT NULL,
    admin text NOT NULL,
    participants text NOT NULL,
    publickey text NOT NULL
);


ALTER TABLE public.grp_modified OWNER TO postgres;

--
-- Name: msg_stack; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.msg_stack (
    to_name text NOT NULL,
    msg bytea NOT NULL,
    is_image integer,
    time_stamp integer NOT NULL
);


ALTER TABLE public.msg_stack OWNER TO postgres;

--
-- Name: clients clients_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.clients
    ADD CONSTRAINT clients_pkey PRIMARY KEY (name);


--
-- Name: grp_modified pk_grp_modified; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grp_modified
    ADD CONSTRAINT pk_grp_modified PRIMARY KEY (grpname, admin, participants, publickey);


--
-- Name: msg_stack pk_msg_stack; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.msg_stack
    ADD CONSTRAINT pk_msg_stack PRIMARY KEY (to_name, msg, time_stamp);


--
-- PostgreSQL database dump complete
--

