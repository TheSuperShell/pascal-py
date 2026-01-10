program br_cont;
    type age: integer;
    var i: char;
begin
    for i := 'a' to 'z' do
        begin
            if i = 'h' then break;
            writeln(i);
        end
end.