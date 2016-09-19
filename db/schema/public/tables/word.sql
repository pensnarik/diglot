create table word (
    id serial,
    language language_mnemonic not null,
    word character varying not null
);

alter table only word
    add constraint word_language_fkey foreign key (language) references lang(id);

alter table only word
    add constraint word_word_key unique (word);

alter table only word
    add constraint word_pkey primary key (id);

