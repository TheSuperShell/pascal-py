program br_cont;
    const PI = 3.14;
    type 
        numbers = (one, two, three);
        other_type = one..two;
    var 
        values: other_type;
begin
    values := three;
    writeln(values);
end.