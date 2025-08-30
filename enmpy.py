import sys

k = 9 * 10^9
print("Scientific Notation:1.23e4")

option = 0
try:
    option = int(input("1: Coulomb's Law\n0: Exit\n"))
except ValueError:
    print("Input a number! Rerun this program.")

if option == 0:
    sys.exit(0)
elif option == 1:
    solve = 0
    try:
        solve = int(input("1: Force\n2: Charge\n3: Distance\n4: Constant\n5: Net force\n"))
    except ValueError:
        print("Input a number! Rerun this program.")
    if solve == 1:
        try:
            qA = abs(float(input("qA: ")))
            qB = abs(float(input("qB: ")))
            r = float(input("r: "))
            print((k * qA * qB) / (r * r))
        except ValueError:
            print("Input numbers!")