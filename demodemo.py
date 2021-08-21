def demo(n, *args, **kwargs):
  print("args : ",args)
  print("kwargs : ",kwargs)
  

demo(1,[1,2,3],name="joe",age=19)