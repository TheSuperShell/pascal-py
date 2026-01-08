program Main;

procedure Alpha(a : integer; b : integer);
var x : integer;
var val: integer;

   procedure Beta(a : integer; b : integer);
   var x : integer;
   begin
      x := a * 10 + b * 2 + val;
      exit;
      x := x * 2;
   end;

begin
   x := (a + b ) * 2;
   val := 10;

   Beta(5, 10);      { procedure call }
end;

begin { Main }

   Alpha(3 + 5, 7);  { procedure call }

end.  { Main }