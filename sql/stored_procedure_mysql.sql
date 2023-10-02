-- Stored procedure
-- Note: Unfortunately SQLite doesn't support stored procedures
-- Here is the stored procedure in MySQL syntax:
DELIMITER //
CREATE PROCEDURE get_avg_borrow_days(
	IN book_id int,
	OUT num_days decimal(6,2)
)
BEGIN
	select avg(TIMESTAMPDIFF(DAY, bb.borrow_date, bb.return_date))
	into num_days
	from borrowed_books as bb
	where bb.book_id=book_id
	and return_date is not null;
END //
DELIMITER ;

-- Example call:
call get_avg_borrow_days(1, @num_days);
select @num_days;
