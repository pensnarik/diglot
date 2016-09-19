create or replace
function get_current_word(auser_id integer) returns character varying as $$
    select w.word from job j join word w on w.id = j.word_id where j.status = 'answering' and j.user_id = auser_id;
$$ language sql security definer;

