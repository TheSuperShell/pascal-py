program br_cont;
    type age: integer;
    var i: char;
        my_age: age;
begin
    my_age := 25;
    writeln('My age is ', my_age + 1);
    for i := 'a' to 'z' do
        begin
            if i = 'h' then break;
            writeln(i);
        end
end.