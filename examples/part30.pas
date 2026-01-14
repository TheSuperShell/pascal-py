program arr;
    const PI = 3.14;
    type 
        example_arr = array[0..10] of array['a'..'z'] of string;
    var a: example_arr;
begin
    a[5, 'f'] := 'Hello';
    writeln(a[5, 'f'])
end.