-- Query to select top 10 most borrowed books
select bb.book_id, b.title, b.author, b.publication_year, b.isbn, count(*) as nr_times_borrowed
from borrowed_books as bb
join books as b
on b.book_id = bb.book_id
group by bb.book_id
order by nr_times_borrowed desc
limit 10;

-- Stored procedure
-- Note: Unfortunately SQLite doesn't support stored procedures
-- See stored_procedure_mysql.sql for the procedure in MySQL syntax

-- Query to find user with most borrowed books
select user_id, count(book_id) as book_count
from (select distinct bb.user_id, bb.book_id from borrowed_books as bb)
group by user_id
order by book_count desc
limit 1;

-- Create index on publication_year
create index idx_books_publication_year on books(publication_year);

-- Query to select all books not borrowed by users published in 2020
select *
from books
where books.book_id
not in (select distinct book_id from borrowed_books)
and publication_year = 2020;

-- Query to select users who borrowed from specific author (e.g.: J.K. Rowling)
select distinct u.user_id, u.first_name, u.last_name, u.email, u.registration_date
from borrowed_books as bb
join books as b
on b.book_id = bb.book_id
join users as u
on bb.user_id = u.user_id
where b.author = 'J.K. Rowling';

-- Create trigger to update return date
create trigger update_return_date
	after insert on borrowed_books
	when new.return_date is null
begin
	update borrowed_books
	set return_date = datetime('now')
	where borrowed_books.borrow_id = new.borrow_id;
end;

