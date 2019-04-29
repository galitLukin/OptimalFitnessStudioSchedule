using JuMP, JuMPeR, Gurobi, DataFrames
using MLDataUtils

D = 7
T = 28
C = 8
I = 18
A = 12
L = 10
U = 50

#classes = ["HOT 26", "HOT 26 FLOW", "SILENT HOT 26", "HOT 26+", "INFERNO HOT PILATES", "INFERNO HOT PILATES LEVEL II", "HOT HATHA FUSION", "HOT HATHA SCULPT"]
#instructors = ["ANCIVAL, SOPHIE", "BOU-NASSIF, JASMINE", "BOUJOULIAN, RACHELLE", "CATES, SHELLEY", "EVANGELISTI, MEREDITH", "HEIRTZLER, LESLIE", "JONES, JACLYN", "LAMBERT, LUCAS", "LANSING, LUCAS", "LOVERME, KYLA", "MCGRATH, SHARON", "MONROE, KYLAH", "PHAN, STEVEN", "PIGOTT, ELLEN", "SERRANO, JIMMY", "STERN, BRIAN", "VEERAPEN, KUMAR", "WOODS, TESS"]

function _solve()
    model = RobustModel(solver=GurobiSolver(OutputFlag=0))
    # if scheduled or not
    @variable(model, x[1:D,1:T,1:C,1:I], Bin)
    @variable(model, y)

    @objective(model, Max, y)
    # this will be robust - comes from objective function
    @constraint(model, y <= sum(A*x[d,t,c,i] for d=1:D, t=1:T, c=1:C, i=1:I))

    # How many class types per day/week
    for d in 1:D
        @constraint(model, sum(x[d,t,1,i] for t=1:T, i=1:I) >= 2)
        @constraint(model, sum(x[d,t,5,i] for t=1:T, i=1:I) >= 1)
    end
    @constraint(model, sum(x[d,t,2,i] for d=1:D, t=1:T, i=1:I) >= 1)
    @constraint(model, sum(x[d,t,3,i] for d=1:D, t=1:T, i=1:I) >= 1)
    @constraint(model, sum(x[d,t,3,i] for d=1:D, t=1:T, i=1:I) <= 2)
    @constraint(model, sum(x[d,t,4,i] for d=1:D, t=1:T, i=1:I) == 1)
    @constraint(model, sum(x[d,t,6,i] for d=1:D, t=1:T, i=1:I) >= 2)
    @constraint(model, sum(x[d,t,7,i] for d=1:D, t=1:T, i=1:I) >= 5)
    @constraint(model, sum(x[d,t,8,i] for d=1:D, t=1:T, i=1:I) >= 5)

    # Instructor schedule constraints
    Availability = readtable("Data/InstructorAvailability.csv", header=true, makefactors=true)
    for d in 1:D
        for i in 1:I
            row = (d-1)*I + i
            for t in 1:T
                col = t + 2
                if Availability[row,col] == 0
                    for c in 1:C
                        @constraint(model, x[d,t,c,i] == 0)
                    end
                end
            end
        end
    end

    # Instructor special schedule constraints
    # shelly - at least one day off
    @variable(model, shelly[1:D], Bin)
    for d in 1:D
        for t in 1:T
            for c in 1:C
                @constraint(model, x[d,t,c,4] <=  shelly[d])
            end
        end
    end
    @constraint(model, sum(shelly[d] for d in 1:D) <= 6)
    # lucas lambert - at most one more evening thats not wednesday or saturday
    variable(model, lucas[1:5], Bin)
    d_ = 1
    for d in [1,2,4,5,7]
        for t in 24:T
            #only does hot 26
            @constraint(model, x[d,t,1,8] <=  lucas[d_])
        end
        d_ = d_ + 1
    end
    @constraint(model, sum(lucas[d] for d in 1:5) <= 1)

    # Instructor class type constraints
    IC = readtable("Data/IntstructorClass.csv", header=true, makefactors=true)
    for c in 1:C
        for i in 1:I
            if IC[i,c+1] == 0
                for d in 1:D
                    for t in 1:T
                        @constraint(model, x[d,t,c,i] == 0)
                    end
                end
            end
        end
    end
    # studio feasibility constraints
    for d in 1:D
        for t in 1:T
            for c in 1:C
                # every day, time, and class type, there is at most one instructor
                @constraint(model, sum(x[d,t,c,i] for i=1:I) <= 1)
            end
            for i in 1:I
                # every day, time, and instructor, there is at most one class type
                @constraint(model, sum(x[d,t,c,i] for c=1:C) <= 1)
            end
        end
    end

    # two classes can't occur at the same time
    for d in 1:D
        for t in 1:T-3
            for i in 1:I
                for i_ in 1:I
                    for c_ in 1:C
                        # one and half hour classes
                        for c in 1:4
                            for t_ in 1:3
                                @constraint(model, x[d,t,c,i] <= 1 - x[d,t+t_,c_,i_])
                            end
                        end
                        # one hour classes
                        for c in 5:8
                            for c in 1:4
                                for t_ in 1:2
                                    @constraint(model, x[d,t,c,i] <= 1 - x[d,t+t_,c_,i_])
                                end
                            end
                        end
                    end
                end
            end
        end
    end
    # 19:30 can one be a one hour class
    for d in 1:D
        for i in 1:I
            for c in 1:4
                @constraint(model, x[d,28,c,i] == 0)
            end
        end
    end
    # same as above for last classes of day
    for d in 1:D
        for t in 26:T-1
            for i in 1:I
                for i_ in 1:I
                    for c_ in 1:C
                        for c in 1:C
                            for t_ in 1:T-t
                                @constraint(model, x[d,t,c,i] <= 1 - x[d,t+t_,c_,i_])
                            end
                        end
                    end
                end
            end
        end
    end

    # this will be robust
    # max/min in each class
    for d in 1:D
        for t in 1:T
            for c in 1:C
                for i in 1:I
                    @constraint(model, L*x[d,t,c,i] <= A)
                    @constraint(model, A*x[d,t,c,i] <= U)
                end
            end
        end
    end

    solve(model)
    xVals = getvalue(x)
    objective = getobjectivevalue(model)
    return xVals, objective
end

xVals, obj = _solve()
println(obj)
println(xVals)
