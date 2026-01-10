program br_cont;
    const PI = 3.14;
    type age = integer;
        other_age = age;
        some_range = 0..10;
    var i: char;
        my_age: other_age;
        range_test: some_range;
    procedure test_range(a: 0..10);
    begin
    end;
begin
    my_age := 25;
    range_test := 5;
    test_range(25);
    writeln(range_test);
    writeln('My age + PI is ', my_age + PI);
    for i := 'a' to 'z' do
        begin
            if i = 'h' then break;
            writeln(i);
        end
end.