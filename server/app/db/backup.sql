--
-- PostgreSQL database dump
--

-- Dumped from database version 16.4
-- Dumped by pg_dump version 16.4

-- Started on 2024-09-04 22:45:09

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
-- TOC entry 2 (class 3079 OID 16451)
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- TOC entry 4841 (class 0 OID 0)
-- Dependencies: 2
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


--
-- TOC entry 867 (class 1247 OID 16608)
-- Name: new_statusenum; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.new_statusenum AS ENUM (
    'INITIALIZED',
    'PROMPT_SAVED',
    'PROMPT_UPDATED',
    'PROMPT_DELETED',
    'COMPLETED',
    'IN_PROGRESS',
    'FAILED'
);


ALTER TYPE public.new_statusenum OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 223 (class 1259 OID 16852)
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO postgres;

--
-- TOC entry 218 (class 1259 OID 16471)
-- Name: prompts_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.prompts_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.prompts_id_seq OWNER TO postgres;

--
-- TOC entry 222 (class 1259 OID 16563)
-- Name: prompts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.prompts (
    id bigint DEFAULT nextval('public.prompts_id_seq'::regclass) NOT NULL,
    prompt text NOT NULL,
    status character varying(30),
    "user" bigint NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    uuid uuid DEFAULT public.uuid_generate_v4()
);


ALTER TABLE public.prompts OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 16475)
-- Name: prompts_user_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.prompts_user_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.prompts_user_seq OWNER TO postgres;

--
-- TOC entry 220 (class 1259 OID 16488)
-- Name: user_context_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.user_context_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_context_id_seq OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 16543)
-- Name: user_context; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_context (
    id bigint DEFAULT nextval('public.user_context_id_seq'::regclass) NOT NULL,
    created timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    context_data jsonb,
    thread_id bigint,
    "user" bigint
);


ALTER TABLE public.user_context OWNER TO postgres;

--
-- TOC entry 217 (class 1259 OID 16400)
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id bigint NOT NULL,
    username character varying(50) NOT NULL,
    email character varying(100) NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    last_login timestamp without time zone
);


ALTER TABLE public.users OWNER TO postgres;

--
-- TOC entry 216 (class 1259 OID 16399)
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO postgres;

--
-- TOC entry 4842 (class 0 OID 0)
-- Dependencies: 216
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- TOC entry 4663 (class 2604 OID 16535)
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- TOC entry 4835 (class 0 OID 16852)
-- Dependencies: 223
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.alembic_version (version_num) FROM stdin;
341fa5b68027
\.


--
-- TOC entry 4834 (class 0 OID 16563)
-- Dependencies: 222
-- Data for Name: prompts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.prompts (id, prompt, status, "user", created_at, uuid) FROM stdin;
300	Write a brainfuck coe snippet	INITIALIZED	1	2024-09-04 18:31:39.68626	85a8e576-d6b9-411e-a5fe-205855b55397
301	Erzäjle einen witz	INITIALIZED	1	2024-09-04 18:56:44.92969	8db2771f-6f1e-4f46-a5b1-d0e7ef3b8338
302		INITIALIZED	1	2024-09-04 19:01:58.863123	0bec562a-88b2-4a74-8e48-9f1b62c852a4
303	Was zum lachen	INITIALIZED	1	2024-09-04 19:04:24.931988	3cb05bb9-9a29-495a-8577-e4b658026b6d
304	Und noch einen bitte	INITIALIZED	1	2024-09-04 19:08:32.4719	649f6314-5aae-4930-80f6-2f8fb67616c3
305	Gerne doch	INITIALIZED	1	2024-09-04 19:14:27.832455	609f2e56-0b1d-483f-b93e-c4e90f51cb78
306	Hahah. Nice	INITIALIZED	1	2024-09-04 19:14:38.6673	e94bfee7-fab6-4cbf-9fd9-317077297d34
307	asdsd asds	INITIALIZED	1	2024-09-04 19:15:18.958541	f40be331-2cdb-45b4-942b-30d72b172aa8
308	asdsa asdsad	INITIALIZED	1	2024-09-04 19:15:50.010608	3127f439-bf70-44d0-a638-0a9566b6c6c7
309	Erkläre auf deutsch\nINFO  [alembic.runtime.migration] Context impl PostgresqlImpl.\nINFO  [alembic.runtime.migration] Will assume transactional DDL.\nINFO  [alembic.autogenerate.compare] Detected removed index 'idx_prompts_status' on 'prompts'\nINFO  [alembic.autogenerate.compare] Detected removed index 'idx_prompts_user' on 'prompts'\nINFO  [alembic.autogenerate.compare] Detected removed index 'idx_prompts_uuid' on 'prompts'\nINFO  [alembic.autogenerate.compare] Detected removed table 'prompts'\nINFO  [alembic.autogenerate.compare] Detected removed index 'idx_username' on 'users'\nINFO  [alembic.autogenerate.compare] Detected removed table 'users'\nINFO  [alembic.autogenerate.compare] Detected removed table 'user_context'\nGenerating C:\\projects\\hudini\\server\\app\\db\\migrations\\versions\\341fa5b68027_initial_migration.py ...	INITIALIZED	1	2024-09-04 20:27:10.415059	66c5b7fe-3ecd-4dd2-923a-b5c00803c713
\.


--
-- TOC entry 4833 (class 0 OID 16543)
-- Dependencies: 221
-- Data for Name: user_context; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.user_context (id, created, updated, context_data, thread_id, "user") FROM stdin;
273	2024-09-04 18:32:58.586596+02	2024-09-04 20:27:10.424062+02	[{"user": 1, "model": null, "prompt": "Write a brainfuck coe snippet", "status": "INITIALIZED", "completion": null}, {"user": null, "model": "gpt-4o-mini", "prompt": null, "status": null, "completion": {"id": "chatcmpl-A3p6C9cr9uckvgqlcrQcpGiEsqIjO", "model": "gpt-4o-mini", "usage": {"ended": 1725467575, "started": 1725467405, "total_tokens": 116, "prompt_tokens": 5, "completion_tokens": 111}, "object": "chat.completion.chunk", "choices": [{"index": 0, "message": {"role": "assistant", "content": "Certainly! Here's a simple Brainfuck code snippet that outputs the letter \\"A\\":\\n\\n```brainfuck\\n++++++++++[>+++++++>++++++++++>+++<<<-]>++.>+.+++++++..+++.>>>++++++++++.\\n```\\n\\n### Explanation:\\n- The code initializes a memory cell with the value 10 (using `++++++++++`).\\n- It then enters a loop (`[>+++++++>++++++++++>+++<<<-]`) that sets up three memory cells with the values 70, 100, and 30 respectively.\\n- After exiting the loop, it uses the `>` command to move to the first cell and outputs the character corresponding to the ASCII value (which is 65 for \\"A\\") using `>++.`.\\n\\nYou can run this code in any Brainfuck interpreter to see the output. If you have any specific requests or need more complex examples, feel free to ask!", "refusal": null}, "logprobs": null, "finish_reason": "null"}], "created": 1725474772, "system_fingerprint": null}}, {"user": null, "model": "gpt-4o", "prompt": null, "status": null, "completion": {"id": "chatcmpl-A3p6EIeOSY1stUxSHsxeNQtWmsc6L", "model": "gpt-4o", "usage": {"ended": 1725467578, "started": 1725467405, "total_tokens": 161, "prompt_tokens": 5, "completion_tokens": 156}, "object": "chat.completion.chunk", "choices": [{"index": 0, "message": {"role": "assistant", "content": "Sure! Here's a simple Brainfuck code snippet that outputs the character 'A':\\n\\n```brainfuck\\n++++++++++       // Set cell 0 to 10\\n[                // Start loop\\n    >+++++++     // Increment cell 1 by 7\\n    <           // Move back to cell 0\\n    -           // Decrement cell 0 by 1\\n]                // End loop when cell 0 is 0\\n>                // Move to cell 1\\n.                // Output the character in cell 1 (ASCII 65, which is 'A')\\n```\\n\\nThis code works as follows:\\n1. It initializes cell 0 to 10.\\n2. It enters a loop that runs 10 times (since cell 0 starts at 10).\\n3. In each iteration of the loop, it increments cell 1 by 7.\\n4. After the loop, cell 1 contains 70 (7 * 10).\\n5. It then moves to cell 1 and outputs its value as an ASCII character, which is 'A'.\\n\\nFeel free to ask if you have any questions or need further assistance", "refusal": null}, "logprobs": null, "finish_reason": "null"}], "created": 1725474774, "system_fingerprint": null}}, {"user": 1, "model": null, "prompt": "Erzäjle einen witz", "status": "INITIALIZED", "completion": null}, {"user": null, "model": "gpt-4o-mini", "prompt": null, "status": null, "completion": {"id": "chatcmpl-A3pSq52tfj02jkWMtZNSWJw0bWFX0", "model": "gpt-4o-mini", "usage": {"ended": 1725468977, "started": 1725467405, "total_tokens": 23, "prompt_tokens": 3, "completion_tokens": 20}, "object": "chat.completion.chunk", "choices": [{"index": 0, "message": {"role": "assistant", "content": "Klar, hier ist ein Witz für dich:\\n\\nWarum können Geister so schlecht lügen?\\n\\nWeil man durch sie hindurchsehen kann! 👻😄", "refusal": null}, "logprobs": null, "finish_reason": "null"}], "created": 1725476176, "system_fingerprint": null}}, {"user": null, "model": "gpt-4o", "prompt": null, "status": null, "completion": {"id": "chatcmpl-A3pSvEfXYj0Ty52ywFMQoI1RpZRbE", "model": "gpt-4o", "usage": {"ended": 1725469004, "started": 1725467405, "total_tokens": 22, "prompt_tokens": 3, "completion_tokens": 19}, "object": "chat.completion.chunk", "choices": [{"index": 0, "message": {"role": "assistant", "content": "Natürlich! Hier ist ein Witz für dich:\\n\\nWarum können Geister so schlecht lügen?\\n\\nWeil man direkt durch sie hindurchsieht", "refusal": null}, "logprobs": null, "finish_reason": "null"}], "created": 1725476181, "system_fingerprint": null}}, {"user": 1, "model": null, "prompt": "", "status": "INITIALIZED", "completion": null}, {"user": null, "model": "gpt-4o-mini", "prompt": null, "status": null, "completion": {"id": "chatcmpl-A3pYKmbIaWML4PASuZef4kl7uxfDi", "model": "gpt-4o-mini", "usage": {"ended": 1725469318, "started": 1725467405, "total_tokens": 44, "prompt_tokens": 3, "completion_tokens": 41}, "object": "chat.completion.chunk", "choices": [{"index": 0, "message": {"role": "assistant", "content": "Natürlich! Hier ist ein Witz für dich:\\n\\nWarum können Geister so schlecht lügen?\\n\\nWeil man durch sie hindurchsehen kann! 👻\\n\\nIch hoffe, das hat dir ein Lächeln ins Gesicht gezaubert! Wenn du mehr Witze oder etwas anderes möchtest, sag einfach Bescheid!", "refusal": null}, "logprobs": null, "finish_reason": "null"}], "created": 1725476516, "system_fingerprint": null}}, {"user": 1, "model": null, "prompt": "Was zum lachen", "status": "INITIALIZED", "completion": null}, {"user": null, "model": "gpt-4o-mini", "prompt": null, "status": null, "completion": {"id": "chatcmpl-A3paca1vPXQA3FlPs3OFTqcIaE4GF", "model": "gpt-4o-mini", "usage": {"ended": 1725469461, "started": 1725467405, "total_tokens": 40, "prompt_tokens": 3, "completion_tokens": 37}, "object": "chat.completion.chunk", "choices": [{"index": 0, "message": {"role": "assistant", "content": "Natürlich! Hier ist ein Witz für dich:\\n\\nWarum können Geister so schlecht lügen?\\n\\nWeil man durch sie hindurchsehen kann! \\n\\nIch hoffe, das bringt dich zum Lachen! Wenn du mehr Witze oder etwas anderes möchtest, sag einfach Bescheid!", "refusal": null}, "logprobs": null, "finish_reason": "null"}], "created": 1725476658, "system_fingerprint": null}}, {"user": null, "model": "gpt-4o", "prompt": null, "status": null, "completion": {"id": "chatcmpl-A3pafXpXez5xepPEQrSyEWLNrXPsd", "model": "gpt-4o", "usage": {"ended": 1725469464, "started": 1725467405, "total_tokens": 33, "prompt_tokens": 3, "completion_tokens": 30}, "object": "chat.completion.chunk", "choices": [{"index": 0, "message": {"role": "assistant", "content": "Klar, hier ist ein Witz für dich:\\n\\nWarum können Geister so schlecht lügen?\\n\\nWeil man direkt durch sie hindurchsieht! 👻😄\\n\\nIch hoffe, das hat dir ein Lächeln ins Gesicht gezaubert", "refusal": null}, "logprobs": null, "finish_reason": "null"}], "created": 1725476661, "system_fingerprint": null}}, {"user": 1, "model": null, "prompt": "Und noch einen bitte", "status": "INITIALIZED", "completion": null}, {"user": null, "model": "gpt-4o-mini", "prompt": null, "status": null, "completion": {"id": "chatcmpl-A3pefPNMm0gJuk1d0QmIkLkhNLHAE", "model": "gpt-4o-mini", "usage": {"ended": 1725469711, "started": 1725467405, "total_tokens": 23, "prompt_tokens": 4, "completion_tokens": 19}, "object": "chat.completion.chunk", "choices": [{"index": 0, "message": {"role": "assistant", "content": "Natürlich! Was kann ich für dich tun? Brauchst du Informationen, eine Geschichte oder etwas anderes? Lass es mich wissen!", "refusal": null}, "logprobs": null, "finish_reason": "null"}], "created": 1725476909, "system_fingerprint": null}}, {"user": null, "model": "gpt-4o", "prompt": null, "status": null, "completion": {"id": "chatcmpl-A3peh8IBnoEpx3YBpoVd5ZGQNHAPg", "model": "gpt-4o", "usage": {"ended": 1725469712, "started": 1725467405, "total_tokens": 10, "prompt_tokens": 4, "completion_tokens": 6}, "object": "chat.completion.chunk", "choices": [{"index": 0, "message": {"role": "assistant", "content": "Natürlich! Wie kann ich Ihnen weiterhelfen", "refusal": null}, "logprobs": null, "finish_reason": "null"}], "created": 1725476911, "system_fingerprint": null}}, {"user": 1, "model": null, "prompt": "Gerne doch", "status": "INITIALIZED", "completion": null}, {"user": null, "model": "gpt-4o-mini", "prompt": null, "status": null, "completion": {"id": "chatcmpl-A3pkPXwT1KV099bNCJLIM90MYdH6K", "model": "gpt-4o-mini", "usage": {"ended": 1725470066, "started": 1725467405, "total_tokens": 7, "prompt_tokens": 2, "completion_tokens": 5}, "object": "chat.completion.chunk", "choices": [{"index": 0, "message": {"role": "assistant", "content": "Wie kann ich Ihnen helfen?", "refusal": null}, "logprobs": null, "finish_reason": "null"}], "created": 1725477265, "system_fingerprint": null}}, {"user": null, "model": "gpt-4o", "prompt": null, "status": null, "completion": {"id": "chatcmpl-A3pkQsDkLF3XX9wIOWkLznS1HKVhs", "model": "gpt-4o", "usage": {"ended": 1725470067, "started": 1725467405, "total_tokens": 8, "prompt_tokens": 2, "completion_tokens": 6}, "object": "chat.completion.chunk", "choices": [{"index": 0, "message": {"role": "assistant", "content": "Natürlich! Wie kann ich Ihnen helfen?", "refusal": null}, "logprobs": null, "finish_reason": "null"}], "created": 1725477266, "system_fingerprint": null}}, {"user": 1, "model": null, "prompt": "Hahah. Nice", "status": "INITIALIZED", "completion": null}, {"user": null, "model": "gpt-4o-mini", "prompt": null, "status": null, "completion": {"id": "chatcmpl-A3pkaVjj9KRUIX3lMndrGhZEHDCGS", "model": "gpt-4o-mini", "usage": {"ended": 1725470077, "started": 1725467405, "total_tokens": 12, "prompt_tokens": 2, "completion_tokens": 10}, "object": "chat.completion.chunk", "choices": [{"index": 0, "message": {"role": "assistant", "content": "I'm glad you found something amusing! What made you laugh?", "refusal": null}, "logprobs": null, "finish_reason": "null"}], "created": 1725477276, "system_fingerprint": null}}, {"user": null, "model": "gpt-4o", "prompt": null, "status": null, "completion": {"id": "chatcmpl-A3pkbJVlC99EATjXz9ASB1K8JebcH", "model": "gpt-4o", "usage": {"ended": 1725470078, "started": 1725467405, "total_tokens": 13, "prompt_tokens": 2, "completion_tokens": 11}, "object": "chat.completion.chunk", "choices": [{"index": 0, "message": {"role": "assistant", "content": "I'm glad you think so! How can I assist you today", "refusal": null}, "logprobs": null, "finish_reason": "null"}], "created": 1725477277, "system_fingerprint": null}}, {"user": 1, "model": null, "prompt": "asdsd asds", "status": "INITIALIZED", "completion": null}, {"user": null, "model": "gpt-4o-mini", "prompt": null, "status": null, "completion": {"id": "chatcmpl-A3plEPzFMHHkUlLo2HYx56KZPQmA2", "model": "gpt-4o-mini", "usage": {"ended": 1725470117, "started": 1725467405, "total_tokens": 21, "prompt_tokens": 2, "completion_tokens": 19}, "object": "chat.completion.chunk", "choices": [{"index": 0, "message": {"role": "assistant", "content": "It seems like your message might have been a typo or an error. How can I assist you today?", "refusal": null}, "logprobs": null, "finish_reason": "null"}], "created": 1725477316, "system_fingerprint": null}}, {"user": null, "model": "gpt-4o", "prompt": null, "status": null, "completion": {"id": "chatcmpl-A3plFj8m1Dw4Q3D3ExtFcul7X3whU", "model": "gpt-4o", "usage": {"ended": 1725470118, "started": 1725467405, "total_tokens": 20, "prompt_tokens": 2, "completion_tokens": 18}, "object": "chat.completion.chunk", "choices": [{"index": 0, "message": {"role": "assistant", "content": "It looks like your message might be incomplete or contain a typo. How can I assist you today", "refusal": null}, "logprobs": null, "finish_reason": "null"}], "created": 1725477317, "system_fingerprint": null}}, {"user": 1, "model": null, "prompt": "asdsa asdsad", "status": "INITIALIZED", "completion": null}, {"user": null, "model": "gpt-4o-mini", "prompt": null, "status": null, "completion": {"id": "chatcmpl-A3pljPtW6jgoN8vKkkCEOGS3gJpPB", "model": "gpt-4o-mini", "usage": {"ended": 1725470148, "started": 1725467405, "total_tokens": 21, "prompt_tokens": 2, "completion_tokens": 19}, "object": "chat.completion.chunk", "choices": [{"index": 0, "message": {"role": "assistant", "content": "It seems like your message might have been a typo or an error. How can I assist you today?", "refusal": null}, "logprobs": null, "finish_reason": "null"}], "created": 1725477347, "system_fingerprint": null}}, {"user": null, "model": "gpt-4o", "prompt": null, "status": null, "completion": {"id": "chatcmpl-A3plk41JpE1dxTii0LJHEpnEarDXt", "model": "gpt-4o", "usage": {"ended": 1725470149, "started": 1725467405, "total_tokens": 19, "prompt_tokens": 2, "completion_tokens": 17}, "object": "chat.completion.chunk", "choices": [{"index": 0, "message": {"role": "assistant", "content": "It looks like your message might be a typo or incomplete. How can I assist you today", "refusal": null}, "logprobs": null, "finish_reason": "null"}], "created": 1725477348, "system_fingerprint": null}}, {"user": 1, "model": null, "prompt": "asdsa asdsad", "status": "INITIALIZED", "completion": null}, {"user": null, "model": "gpt-4o-mini", "prompt": null, "status": null, "completion": {"id": "chatcmpl-A3q1Tco8dESF2UgvG547nlcCIBxdW", "model": "gpt-4o-mini", "usage": {"ended": 1725471125, "started": 1725467405, "total_tokens": 21, "prompt_tokens": 2, "completion_tokens": 19}, "object": "chat.completion.chunk", "choices": [{"index": 0, "message": {"role": "assistant", "content": "It seems like your message might have been a typo or an error. How can I assist you today?", "refusal": null}, "logprobs": null, "finish_reason": "null"}], "created": 1725478323, "system_fingerprint": null}}, {"user": null, "model": "gpt-4o", "prompt": null, "status": null, "completion": {"id": "chatcmpl-A3q1UIEzIkCDUglYFApCEF557oL9k", "model": "gpt-4o", "usage": {"ended": 1725471126, "started": 1725467405, "total_tokens": 19, "prompt_tokens": 2, "completion_tokens": 17}, "object": "chat.completion.chunk", "choices": [{"index": 0, "message": {"role": "assistant", "content": "It looks like your message might be a typo or incomplete. How can I assist you today", "refusal": null}, "logprobs": null, "finish_reason": "null"}], "created": 1725478324, "system_fingerprint": null}}, {"user": 1, "model": null, "prompt": "Write a brainfuck coe snippet", "status": "INITIALIZED", "completion": null}, {"user": 1, "model": null, "prompt": "Write a brainfuck coe snippet", "status": "INITIALIZED", "completion": null}, {"user": 1, "model": null, "prompt": "asdsa asdsad", "status": "INITIALIZED", "completion": null}, {"user": null, "model": "gpt-4o-mini", "prompt": null, "status": null, "completion": {"id": "chatcmpl-A3qrEVSAs4QAh44ireh8TU3FP6dwE", "model": "gpt-4o-mini", "usage": {"ended": 1725474332, "started": 1725474307, "total_tokens": 21, "prompt_tokens": 2, "completion_tokens": 19}, "object": "chat.completion.chunk", "choices": [{"index": 0, "message": {"role": "assistant", "content": "It seems like your message might have been a typo or an error. How can I assist you today?", "refusal": null}, "logprobs": null, "finish_reason": "null"}], "created": 1725481532, "system_fingerprint": null}}, {"user": null, "model": "gpt-4o", "prompt": null, "status": null, "completion": {"id": "chatcmpl-A3qrEQcphOB0eALMLDFBPp8SvgTSz", "model": "gpt-4o", "usage": {"ended": 1725474333, "started": 1725474307, "total_tokens": 19, "prompt_tokens": 2, "completion_tokens": 17}, "object": "chat.completion.chunk", "choices": [{"index": 0, "message": {"role": "assistant", "content": "It looks like your message might be a typo or incomplete. How can I assist you today?", "refusal": null}, "logprobs": null, "finish_reason": "null"}], "created": 1725481532, "system_fingerprint": null}}, {"user": 1, "model": null, "prompt": "Was zum lachen", "status": "INITIALIZED", "completion": null}, {"user": null, "model": "gpt-4o-mini", "prompt": null, "status": null, "completion": {"id": "chatcmpl-A3qrJ0tjWFaFiairgMwaKoLmX1I3B", "model": "gpt-4o-mini", "usage": {"ended": 1725474338, "started": 1725474307, "total_tokens": 40, "prompt_tokens": 3, "completion_tokens": 37}, "object": "chat.completion.chunk", "choices": [{"index": 0, "message": {"role": "assistant", "content": "Natürlich! Hier ist ein Witz für dich:\\n\\nWarum können Geister so schlecht lügen?\\n\\nWeil man durch sie hindurchsehen kann! \\n\\nIch hoffe, das bringt dich zum Lachen! Wenn du mehr Witze oder etwas anderes möchtest, sag einfach Bescheid!", "refusal": null}, "logprobs": null, "finish_reason": "null"}], "created": 1725481537, "system_fingerprint": null}}, {"user": null, "model": "gpt-4o", "prompt": null, "status": null, "completion": {"id": "chatcmpl-A3qrKYPpDUHxQ1bb5PdAs92lwRVCa", "model": "gpt-4o", "usage": {"ended": 1725474339, "started": 1725474307, "total_tokens": 33, "prompt_tokens": 3, "completion_tokens": 30}, "object": "chat.completion.chunk", "choices": [{"index": 0, "message": {"role": "assistant", "content": "Klar, hier ist ein Witz für dich:\\n\\nWarum können Geister so schlecht lügen?\\n\\nWeil man direkt durch sie hindurchsieht! 👻😄\\n\\nIch hoffe, das hat dir ein Lächeln ins Gesicht gezaubert!", "refusal": null}, "logprobs": null, "finish_reason": "null"}], "created": 1725481538, "system_fingerprint": null}}, {"user": 1, "model": null, "prompt": "Write a brainfuck coe snippet", "status": "INITIALIZED", "completion": null}, {"user": null, "model": "gpt-4o-mini", "prompt": null, "status": null, "completion": {"id": "chatcmpl-A3qrTjCwtxtthT4IPVQHih5Dfk17G", "model": "gpt-4o-mini", "usage": {"ended": 1725474349, "started": 1725474307, "total_tokens": 90, "prompt_tokens": 5, "completion_tokens": 85}, "object": "chat.completion.chunk", "choices": [{"index": 0, "message": {"role": "assistant", "content": "Certainly! Here's a simple Brainfuck code snippet that outputs the letter \\"A\\":\\n\\n```brainfuck\\n++++++++++[>+++++++>++++++++++>+++<<<-]>++.>+.+++++++..+++.>>>++++++++++.\\n```\\n\\n### Explanation:\\n- The code initializes a memory cell with the value 10.\\n- It then uses a loop to set up the values for the ASCII characters.\\n- Finally, it outputs the character \\"A\\" (ASCII value 65) followed by a newline.\\n\\nYou can run this code in any Brainfuck interpreter to see the output. If you have any specific requests or need more complex examples, feel free to ask!", "refusal": null}, "logprobs": null, "finish_reason": "null"}], "created": 1725481547, "system_fingerprint": null}}, {"user": null, "model": "gpt-4o", "prompt": null, "status": null, "completion": {"id": "chatcmpl-A3qrVlBkNpQSJimDvMyd763gw5my5", "model": "gpt-4o", "usage": {"ended": 1725474352, "started": 1725474307, "total_tokens": 157, "prompt_tokens": 5, "completion_tokens": 152}, "object": "chat.completion.chunk", "choices": [{"index": 0, "message": {"role": "assistant", "content": "Sure! Here's a simple Brainfuck code snippet that outputs the character 'A':\\n\\n```brainfuck\\n++++++++++       // Set cell 0 to 10\\n[                // Start loop\\n    >+++++++     // Increment cell 1 by 7\\n    <           // Move back to cell 0\\n    -           // Decrement cell 0 by 1\\n]                // End loop when cell 0 is 0\\n>                // Move to cell 1\\n.                // Output the character in cell 1 (which is 65, ASCII for 'A')\\n```\\n\\nThis code works as follows:\\n1. It initializes the first cell (cell 0) to 10.\\n2. It enters a loop that runs 10 times (since cell 0 starts at 10).\\n3. In each iteration of the loop, it increments the second cell (cell 1) by 7.\\n4. After the loop, cell 1 contains the value 70 (10 * 7).\\n5. It then moves to cell 1 and outputs its value as an ASCII character, which is 'A", "refusal": null}, "logprobs": null, "finish_reason": "null"}], "created": 1725481549, "system_fingerprint": null}}, {"user": 1, "model": null, "prompt": "Erkläre auf deutsch\\nINFO  [alembic.runtime.migration] Context impl PostgresqlImpl.\\nINFO  [alembic.runtime.migration] Will assume transactional DDL.\\nINFO  [alembic.autogenerate.compare] Detected removed index 'idx_prompts_status' on 'prompts'\\nINFO  [alembic.autogenerate.compare] Detected removed index 'idx_prompts_user' on 'prompts'\\nINFO  [alembic.autogenerate.compare] Detected removed index 'idx_prompts_uuid' on 'prompts'\\nINFO  [alembic.autogenerate.compare] Detected removed table 'prompts'\\nINFO  [alembic.autogenerate.compare] Detected removed index 'idx_username' on 'users'\\nINFO  [alembic.autogenerate.compare] Detected removed table 'users'\\nINFO  [alembic.autogenerate.compare] Detected removed table 'user_context'\\nGenerating C:\\\\projects\\\\hudini\\\\server\\\\app\\\\db\\\\migrations\\\\versions\\\\341fa5b68027_initial_migration.py ...", "status": "INITIALIZED", "completion": null}]	1	1
\.


--
-- TOC entry 4829 (class 0 OID 16400)
-- Dependencies: 217
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, username, email, created_at, last_login) FROM stdin;
1	john_doe	john@example.com	2024-08-17 15:40:56.660393	\N
68	W077A3lq8M	oYcmYGTPUl@example.com	2024-09-01 17:35:26.688113	\N
71	P4yMZvBpkb	xGmPKrmbOQ@example.com	2024-09-01 17:40:06.646773	\N
74	Mfu8fFPVrS	y2n8IryAQN@example.com	2024-09-01 17:43:03.531493	\N
9	vJbbWSqUrt	hZe1iRzzNR@example.com	2024-09-01 10:53:44.881985	\N
12	k2N9I3pHQu	RjSHY8SsFl@example.com	2024-09-01 10:59:11.468743	\N
78	p4hVRL1bxZ	htB6J2F8RD@example.com	2024-09-01 17:56:33.96151	\N
22	user_132887	user132887@example.com	2024-09-01 13:01:17.891276	\N
90	3SLHLoZXsw	wflTD88W1s@example.com	2024-09-01 18:20:08.15037	\N
95	test_user	test_user@example.com	2024-09-02 05:19:01.984128	\N
96	test_user	test_user@example.com	2024-09-02 05:20:33.786693	\N
34	test_user	test_user@example.com	2024-09-01 15:24:07.193937	\N
35	test_user	test_user@example.com	2024-09-01 15:24:44.788014	\N
36	test_user	test_user@example.com	2024-09-01 15:25:01.691419	\N
37	test_user	test_user@example.com	2024-09-01 15:25:54.231526	\N
38	test_user	test_user@example.com	2024-09-01 15:26:27.803766	\N
39	user_362177	user362177@example.com	2024-09-01 15:38:15.526712	\N
97	test_user	test_user@example.com	2024-09-02 05:22:36.354043	\N
98	cYALE7Nq5Y	a7snX2i37q@example.com	2024-09-02 05:55:56.585948	\N
42	user_524249	user524249@example.com	2024-09-01 15:39:19.922072	\N
43	user_968610	user968610@example.com	2024-09-01 15:39:53.713816	\N
44	user_187806	user187806@example.com	2024-09-01 15:40:04.375734	\N
99	gxlHDPUh6b	yDFaRZK5Or@example.com	2024-09-02 05:57:38.8001	\N
100	XwzhgQVAwx	gBpnfE13rR@example.com	2024-09-02 05:58:57.617448	\N
101	hopgv6zydw	hZuqbrgHBX@example.com	2024-09-02 06:06:55.23822	\N
102	MROhSFPIdv	PvgPJCo2H9@example.com	2024-09-02 06:08:54.742923	\N
103	C9U7DVuUtL	Co2OJMFmO4@example.com	2024-09-02 06:12:56.375469	\N
104	yvztf2eBq3	gTTBXRpzQy@example.com	2024-09-02 06:14:16.334113	\N
106	mu1UmJ5yLt	yBYjTPky9h@example.com	2024-09-02 12:43:34.604279	\N
107	ILu7tpUeo1	mKJwEhSRLj@example.com	2024-09-02 12:46:53.978211	\N
108	dvCzcb4nRo	iSWYVS5XzK@example.com	2024-09-02 12:47:17.576794	\N
109	dgL3KNiTmT	TNovTNmj4Z@example.com	2024-09-02 12:47:40.948672	\N
110	HvMEFOO9c8	mnQfyDDIuJ@example.com	2024-09-02 12:49:33.021557	\N
111	JkVhsLzKpC	xbOfWv5TkF@example.com	2024-09-02 12:50:59.586688	\N
115	CiyVxi8dYU	4kO92AFY65@example.com	2024-09-03 17:52:58.428428	\N
62	uI2q6yDo08	QQ440iQWcF@example.com	2024-09-01 17:26:45.092987	\N
\.


--
-- TOC entry 4843 (class 0 OID 0)
-- Dependencies: 218
-- Name: prompts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.prompts_id_seq', 309, true);


--
-- TOC entry 4844 (class 0 OID 0)
-- Dependencies: 219
-- Name: prompts_user_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.prompts_user_seq', 1, false);


--
-- TOC entry 4845 (class 0 OID 0)
-- Dependencies: 220
-- Name: user_context_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.user_context_id_seq', 273, true);


--
-- TOC entry 4846 (class 0 OID 0)
-- Dependencies: 216
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 115, true);


--
-- TOC entry 4682 (class 2606 OID 16856)
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- TOC entry 4680 (class 2606 OID 16571)
-- Name: prompts prompts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.prompts
    ADD CONSTRAINT prompts_pkey PRIMARY KEY (id);


--
-- TOC entry 4675 (class 2606 OID 16552)
-- Name: user_context user_context_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_context
    ADD CONSTRAINT user_context_pkey PRIMARY KEY (id);


--
-- TOC entry 4673 (class 2606 OID 16537)
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- TOC entry 4676 (class 1259 OID 16577)
-- Name: idx_prompts_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_prompts_status ON public.prompts USING btree (status);


--
-- TOC entry 4677 (class 1259 OID 16578)
-- Name: idx_prompts_user; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_prompts_user ON public.prompts USING btree ("user");


--
-- TOC entry 4678 (class 1259 OID 16590)
-- Name: idx_prompts_uuid; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX idx_prompts_uuid ON public.prompts USING btree (uuid);


--
-- TOC entry 4671 (class 1259 OID 16407)
-- Name: idx_username; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_username ON public.users USING btree (username);


--
-- TOC entry 4683 (class 2606 OID 16558)
-- Name: user_context fk_user_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_context
    ADD CONSTRAINT fk_user_id FOREIGN KEY ("user") REFERENCES public.users(id) ON DELETE CASCADE;


--
-- TOC entry 4684 (class 2606 OID 16572)
-- Name: prompts fk_user_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.prompts
    ADD CONSTRAINT fk_user_id FOREIGN KEY ("user") REFERENCES public.users(id) ON DELETE CASCADE;


-- Completed on 2024-09-04 22:45:10

--
-- PostgreSQL database dump complete
--

