import solver

def main():
    examples = ["(Lx.x(Lx.Ly.y)(Lx.Ly.x))(Lx.Ly.x)",
                "(Lx.x(Lx.Ly.y)(Lx.Ly.x))(Lx.Ly.y)",
                "(Ln.Lm.Lf.Lx.nf(mfx))(Lf.Lx.f(fx))(Lf.Lx.f(f(fx)))",
                "(Ln.Lm.Lf.Lx.n(mf)x)(Lf.Lx.f(fx))(Lf.Lx.f(f(fx)))",
                "(Ln.Lm.Lf.Lx.mnfx)(Lf.Lx.f(fx))(Lf.Lx.f(f(fx)))"
                ]
    print("Example Expressions :")
    for i, ex in enumerate(examples):
        print(f"  {i} : {ex}")
    print("Please type lambda expression or choose example by typing its index :")
    inp = input(" >> ")

    expression = ""
    if inp.isdigit() and int(inp) < len(examples):
        expression = examples[int(inp)]
    else:
        expression = inp
    
    lambda_solver = solver.LambdaSolver(expression, vis=True)

    print(f"Solving expression : {str(lambda_solver.start)} ...")
    success = lambda_solver.solve()
    if success:
        print(f"Solution Found : {str(lambda_solver.solution)}")
    else:
        print("No Solution Found after 1000 iterations...")


if __name__ == "__main__":
    main()
