import sys
import math

k = 9e9         # Coulomb Constant
vps = 8.85e-12  # Vacuum Permittivity of Space
pi = 3.14159265358979
print("Scientific Notation:1.23e4")

option = 0
try:
    option = int(input("1: Coulomb's Law\n2: Gauss's Law\n0: Exit\n"))
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
elif option==2:
    print("Flux = q_enc / vacuum permittivity")
    try:
        solve = int(input("1: Sphere\n2: Cylinder\n3: Plane\n"))
    except ValueError:
        print("enter a number! rerun")
    if(solve == 1):
        print("Let r be Gaussian surface radius, R is charged surface radius")
        try:
            shape = int(input("1: constant r≥R\n2: constant r<R\n3: variable r≥R\n4: variable r<R\n"))
        except ValueError:
            print("enter a number! rerun")
        if shape == 1:
            try:
                mode=int(input("1: q given\n2: p0 given\n"))
                if mode == 1:
                    q=float(input("enter enclosed charge:"))
                    r=float(input("enter Gaussian surface radius:"))
                    print("E=k*q/(r^2)={E}".format(E=k*q/(r*r)))
                elif mode == 2:
                    p=float(input("enter charge density p0:"))
                    R=float(input("enter charged surface radius R:"))
                    r=float(input("enter Gaussian surface radius:"))
                    print("E=(pR^3)/(3Er^2)={E}".format(E=p*R*R*R/(3*vps*r*r)))
            except ValueError:
                print("ValueError")
        elif shape == 2:
            try:
                mode=int(input("1: p0 given\n2: q given\n"))
                if mode == 1:
                    r=float(input("Gaussian surface radius r:"))
                    p=float(input("charge density p0:"))
                    print("E=rp/(3E)={E}".format(E=r*p/(3*vps)))
                elif mode == 2:
                    q=float(input("enter enclosed charge q:"))
                    R=float(input("enter charged surface radius R:"))
                    r=float(input("enter Gaussian surface radius:"))
                    v=4/3*pi*R*R*R
                    p=q/v
                    print("E=rp/(3E)={E}".format(E=r*p/(3*vps)))
            except ValueError:
                print("rerun")
        elif shape == 3:
            print("p(r)=ar^n")
            try:
                a=float(input("(ar^n)a:"))
                n=float(input("(ar^n)n:"))
                R=float(input("charged surface radius R:"))
                r=float(input("Gaussian surface radius r:"))
                print("E=(aR^(n+3))/(Er^2*(n+3))={E}".format(E=(a*R^(n+3))/(vps*r*r*(n+3))))
            except ValueError:
                print("rerun")
        elif shape == 4:
            print("p(r)=ar^n")
            try:
                a=float(input("(ar^n)a:"))
                n=float(input("(ar^n)n:"))
                r=float(input("Gaussian surface radius r:"))
                print("E=(4aR^(n+1))/(E(n+3))={E}".format(E=(a*r^(n+1))/(vps*(n+3))))
            except ValueError:
                print("rerun")
        print("where E is vacuum permittivity of space")
    elif(solve == 2):
        print("coming soon!")
    elif(solve == 3):
        print("comign soon!")