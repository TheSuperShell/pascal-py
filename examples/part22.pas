program Main;
   var res : real;

   function Sum(a : real; b: real) : real;
   begin
      exit(a + b);
   end;

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

   res := Sum(123, 2);
   Alpha(3 + 5, 7);  { procedure call }

end.  { Main }