program fib_1;
    var res: integer;

    function fib(num: integer): integer;
    begin
        if (num <= 1) then
            exit(num);
        exit(fib(num - 1) + fib(num - 2))
    end;

begin

    { res := fib(9);}
    res := TwoNumberSum(10, 24);
end.