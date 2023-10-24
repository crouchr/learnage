from bbfreeze import Freezer
f = Freezer("bbfreeze_test",includes=("bbfreeze_test.py"))
f.addScript("bbfreeze_test_run.py")
f()
