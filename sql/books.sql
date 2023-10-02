create table books (
	book_id integer primary key,
	title text,
	author text,
	publication_year integer,
	isbn text
);

create table users (
	user_id integer primary key,
	first_name text,
	last_name text,
	email text,
	registration_date text
);

create table borrowed_books (
	borrow_id integer primary key,
	user_id integer,
	book_id integer,
	borrow_date text not null,
	return_date text,
	FOREIGN KEY(user_id) REFERENCES users(user_id),
	FOREIGN KEY(book_id) REFERENCES books(book_id)
);

insert into books (title, author, publication_year, isbn) values
('my title1', 'jane', 2020, '1111111'),
('my title 2', 'joe', 2020, '1111111'),
('my title 3', 'joe', 2020, '1111111'),
('my title 4', 'joe', 2020, '1111111'),
('my title 5', 'joe', 2020, '1111111'),
('my title 6', 'joe', 2020, '1111111'),
('my title 7', 'joe', 2020, '1111111'),
('my title 8', 'joe', 2021, '1111111'),
('my title 9', 'J.K. Rowling', 2021, '1111111'),
('my title 10', 'J.K. Rowling', 2021, '1111111'),
('my title 11', 'J.K. Rowling', 2021, '1111111'),
('my title 12', 'J.K. Rowling', 2021, '1111111'),
('my title 13', 'J.K. Rowling', 2020, '1111111'),
('my title 14', 'J.K. Rowling', 2020, '1111111');

insert into users (first_name, last_name, email, registration_date) values
('joe', 'doe', 'joe@bar.com', datetime('now')),
('jane', 'b', 'jane@bar.com', datetime('now')),
('kim', 'foo', 'kim@bar.com', datetime('now'));

insert into borrowed_books (user_id, book_id, borrow_date, return_date) values
(1, 1, datetime('now'), datetime('now', '+3 day')),
(1, 1, datetime('now'), datetime('now', '+3 day')),
(1, 1, datetime('now'), datetime('now', '+3 day')),
(1, 1, datetime('now'), datetime('now', null)),
(1, 2, datetime('now'), datetime('now', '+3 day')),
(1, 2, datetime('now'), datetime('now', '+3 day')),
(1, 3, datetime('now'), datetime('now', '+3 day')),
(1, 4, datetime('now'), datetime('now', '+3 day')),
(1, 5, datetime('now'), datetime('now', '+3 day')),
(2, 5, datetime('now'), datetime('now', '+3 day')),
(2, 5, datetime('now'), datetime('now', '+3 day')),
(2, 5, datetime('now'), datetime('now', '+3 day')),
(2, 5, datetime('now'), datetime('now', null)),
(2, 6, datetime('now'), datetime('now', null)),
(2, 9, datetime('now'), datetime('now', '+6 day')),
(3, 10, datetime('now'), datetime('now', '+3 day')),
(3, 9, datetime('now'), datetime('now', null)),
(3, 7, datetime('now'), datetime('now', null)),
(3, 8, datetime('now'), datetime('now', null)),
(3, 1, datetime('now'), datetime('now', null)),
(3, 12, datetime('now'), datetime('now', null));

