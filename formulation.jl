using JuMP, JuMPeR, Gurobi

include("constraints.jl")

function getSchedule(allA, allSubAsLower, allSubAsUpper)
    model = Model(solver=GurobiSolver(OutputFlag=0))
    # if scheduled or not
    @variable(model, x[1:D,1:T,1:C,1:I], Bin)
    @variable(model, y)

    @objective(model, Max, y)
    for A in allA
        # this will be robust - comes from objective function
        @constraint(model, y <= sum(A[d,t,c,i]*x[d,t,c,i] for d=1:D, t=1:T, c=1:C, i=1:I))
    end

    # How many class types per day/week
    classTypeOccurence(model, x)

    # Instructor schedule constraints
    instructorSchedule(model, x)

    # Instructor special schedule constraints
    instructorSpecialSchedule(model, x)

    # Instructor class type constraints
    instuctorClassType(model, x)

    # studio feasibility constraints
    studio(model, x)

    # max/min in each class
    for d in 1:D
        for t in 1:T
            for c in 1:C
                for i in 1:I
                    ind = (d-1)*4032 + (t-1)*144 + (c-1)*18 + i
                    for A in allSubAsLower[ind]
                        @constraint(model, L*x[d,t,c,i] <= A)
                    end
                    for A in allSubAsUpper[ind]
                        @constraint(model, A*x[d,t,c,i] <= U)
                    end
                end
            end
        end
    end

    solve(model)
    xVals = getvalue(x)
    objective = getobjectivevalue(model)
    return xVals, objective
end
