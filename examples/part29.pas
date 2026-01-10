program br_cont;
    const PI = 3.14;
    type age = integer;
        other_age = age;
        some_range = 0..10;
    var i: char;
        my_age: other_age = 30;
        range_test: some_range = 5;
    procedure test_range(a: 0..10);
    begin
    end;
begin
    range_test := 5;
    writeln(range_test);
    writeln('My age + PI is ', my_age + PI);
    for i := 'a' to 'z' do
        begin
            if i = 'h' then break;
            writeln(i);
        end
end.