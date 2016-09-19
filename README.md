# diglot

## Basic

Diglot is a Telegram Bot which helps you to learn foreign words. It stores a translations as a dictionary
in PostgreSQL database.

The bot knew following commands:
* /new - adds a new traslation into database
* /play - gives you a new word for translation
* /giveup - means that you doesn't know a translation and giving up

## Database

The main entity is dictionary, actually, it stores all translations.

```sql
create table dictionary (
    id serial,
    word_from_id integer not null,
    word_to_id integer not null,
    relation relation_mnemonic not null,
    authority smallint not null,
    user_id integer not null,
    constraint dictionary_authority_check CHECK ((authority > 0))
);
```
