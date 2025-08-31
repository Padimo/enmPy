import sys
import math

k = 9e9
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
            qA = abs(float(input("qA=")))
            qB = abs(float(input("qB=")))
            r = float(input("r="))
            print((k * qA * qB) / (r * r))
        except ValueError:
            print("Input numbers!")
    if solve == 2:
        try:
            F = abs(float(input("F=")))
            qB = abs(float(input("qB=")))
            r = float(input("r="))
            print((F * r * r) / (qB * k))
        except ValueError:
            print("Input numbers!")
    if solve == 3:
        try:
            F = abs(float(input("F=")))
            qA = abs(float(input("qA=")))
            qB = float(input("qB="))
            # F = kqq/rr
            print(math.sqrt((k * qA * qB) / F))
        except ValueError:
            print("Input numbers!")
    if solve == 4:
        try:
            F = abs(float(input("F=")))
            qA = abs(float(input("qA=")))
            qB = float(input("qB="))
            r = float(input("r="))
            print(math.sqrt((F * r * r) / (qA * qB)))
        except ValueError:
            print("Input numbers!")
    if solve == 5:
        try:
            Fx = 0
            Fy = 0
            tc = float(input("test charge="))
            tcx = float(input("test charge x="))
            tcy = float(input("test charge y="))
            q = 1
            while(q != 0):
                print("enter q=0 to exit")
                q = float(input("q="))
                if q==0:
                    break
                qx = float(input("qx="))
                qy = float(input("qy="))
                r = math.sqrt((tcx - qx) ** 2 + (tcy - qy) ** 2)
                try:
                    Fmag = (k * q * tc) / (r * r)
                except:
                    print("test charge and Q at same point!")
                    break
                print("Fmag={x}".format(x=Fmag))
                try:
                    Fx += Fmag * ((tcx-qx)/float(r))
                except:
                    print("no x component")
                try:
                    Fy += Fmag * ((tcy-qy)/float(r))
                except:
                    print("no y component")
                print("Fx={x}\nFy={y}".format(x=Fx, y=Fy))
            print("Fx={x}\nFy={y}".format(x=Fx, y=Fy))
        except ValueError:
            print("Input numbers!")
