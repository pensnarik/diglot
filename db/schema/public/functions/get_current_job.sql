create or replace
function get_current_job(auser_id integer) returns integer as $$
    select id from job where user_id = auser_id and status = 'answering';
$$ language sql security definer;

