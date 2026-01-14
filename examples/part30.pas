program arr;
const PI = 3.14;
    var a: array[0..3] of array[0..3] of real;
    var i: integer;
    var j: integer;
begin
    for i := 0 to 3 do
        for j := 0 to 3 do
            a[i][j] := i * j;
    writeln(a)
end.