using DataFrames, JuMP

function firstUncertainty()
    minVals, maxVals, minWeekly, maxWeekly, dailyMin, dailyMax = calcRanges()
    a = zeros(Int64, D,T,C,I)
    for d in 1:D
        for t in 1:T
            for c in 1:C
                for i in 1:I
                    mi, ma = minVals[d,t,c,i], maxVals[d,t,c,i]
                    if ma > 0
                        a[d,t,c,i] = 55
                    end
                end
            end
        end
    end
    return a
end

function buildUncertainties(obj,x)
    minVals, maxVals, minWeekly, maxWeekly, dailyMin, dailyMax = calcRanges()
    As = []
    i = 1
    feasible, A, objective = wcArrivals(obj, x, minVals, maxVals, minWeekly, maxWeekly, dailyMin, dailyMax)
    if ~feasible && objective >= 1
        push!(As,A)
    end
    return As
end

function wcArrivals(obj, x, minVals, maxVals, minWeekly, maxWeekly, dailyMin, dailyMax)
    # solve worst case min problem - formulate WC
    wc = Model(solver=GurobiSolver(OutputFlag=0))

    @variable(wc, A[1:D,1:T,1:C,1:I]>=0)

    @objective(wc, Max, obj - sum(A[d,t,c,i]*x[d,t,c,i] for d=1:D, t=1:T, c=1:C, i=1:I))
    for d in 1:D
        for t in 1:T
            for c in 1:C
                for i in 1:I
                    @constraint(wc, A[d,t,c,i] >= minVals[d,t,c,i])
                    @constraint(wc, A[d,t,c,i] <= maxVals[d,t,c,i])
                end
            end
        end
    end
    for d in 1:D
        @constraint(wc, sum(A[d,t,c,i]*x[d,t,c,i] for t=1:T, c=1:C, i=1:I) >= dailyMin[d])
    end
    @constraint(wc, sum(A[d,t,c,i]*x[d,t,c,i] for d=1:D, t=1:T, c=1:C, i=1:I) >= minWeekly)
    solve(wc)
    aVals = getvalue(A)
    objective = getobjectivevalue(wc)
    if objective > 0
        return false, aVals, objective
    end
    return true, [], objective
end

function calcRanges()
    uMin = readtable("Data/output/staticUMin.csv", header=true, makefactors=true)
    uMax = readtable("Data/output/staticUMin.csv", header=true, makefactors=true)
    minVals = zeros(Int64, D,T,C,I)
    maxVals = zeros(Int64, D,T,C,I)
    for d in 1:D
        for t in 1:T
            for c in 1:C
                for i in 1:I
                    row = (d-1)*T*C + (t-1)*C + c
                    minVals[d,t,c,i] = uMin[row,i]
                    maxVals[d,t,c,i] = uMax[row,i]
                end
            end
        end
    end
    #uDaily = readtable("Data/output/staticUDaily.csv", header=true, makefactors=true)
    uDaily = readtable("Data/output/SARIMAdailyU.csv", header=true, makefactors=true)
    minWeekly, maxWeekly = uDaily[1,:MinVal], uDaily[1,:MaxVal]
    dailyMin = []
    dailyMax = []
    for i=2:8
         push!(dailyMin, uDaily[i,:MinVal])
         push!(dailyMax, uDaily[i,:MaxVal])
    end
    return minVals, maxVals, minWeekly, maxWeekly, dailyMin, dailyMax
end
