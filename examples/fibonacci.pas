program fib_1;
    function fib(num: integer): integer;
    begin
        if (num <= 1) then
            exit(num);
        exit(fib(num - 1) + fib(num - 2))
    end;

begin

    WRITELN(fib(9))
end.