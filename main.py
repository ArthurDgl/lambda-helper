import lambdas

def main():
    expression = lambdas.LambdaExpression("(Ln.Lm.Lf.Lx.nmfx)(Lf.Lx.f(f(x)))(Lf.Lx.f(f(f(x))))")
    print(expression.get_expression())
    # expression.print_tree()

    while True:
        reductions = expression.find_reductions()
        if len(reductions) == 0:
            break
        print(reductions)
        inp = input(" >> ")
        if inp == 'q':
            break
        elif inp == '':
            index = 0
        else:
            index = int(inp)
        
        expression.apply_reduction(reductions[index])
        print(expression.get_expression())


if __name__ == "__main__":
    main()

'''
TODO:

remove scope & bounds system

remake id propagation

implement multi character variables

'''