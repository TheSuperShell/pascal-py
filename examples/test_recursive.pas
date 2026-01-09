Program recurse;
    function test_types: string;
    begin
        test_types := 'hello'
    end;
begin
    writeln(test_types() + ' World')
end.