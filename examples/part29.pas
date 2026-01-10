program br_cont;
    const PI = 3.14;
    type age = integer;
    var i: char;
        my_age: age;
begin
    my_age := 25;
    writeln('My age + PI is ', my_age + PI);
    for i := 'a' to 'z' do
        begin
            if i = 'h' then break;
            writeln(i);
        end
end.