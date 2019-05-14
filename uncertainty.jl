using DataFrames, JuMP

function firstUncertainty()
    minVals, maxVals, minWeekly, maxWeekly, dailyMin, dailyMax = calcRanges()
    a = zeros(Float64, D,T,C,I)
    for d in 1:D
        for t in 1:T
            for c in 1:C
                for i in 1:I
                    mi, ma = minVals[d,t,c,i], maxVals[d,t,c,i]
                    if mi > 0
                        a[d,t,c,i] = 55
                    end
                end
            end
        end
    end
    return a
end

function buildUncertainties(obj, x, z, alpha)
    minVals, maxVals, minWeekly, maxWeekly, dailyMin, dailyMax = calcRanges()
    As = []
    i = 1
    feasible, A, objective = wcArrivals(obj, x, z, alpha, minVals, maxVals, minWeekly, maxWeekly, dailyMin, dailyMax)
    if ~feasible && objective >= 1
        push!(As,A)
    end
    return As
end

function wcArrivals(obj, x, z, alpha, minVals, maxVals, minWeekly, maxWeekly, dailyMin, dailyMax)
    # solve worst case min problem - formulate WC
    wc = Model(solver=GurobiSolver(OutputFlag=0))

    @variable(wc, A[1:D,1:T,1:C,1:I]>=0)

    @objective(wc, Max, obj - sum(A[d,t,c,i]*x[d,t,c,i] for d=1:D, t=1:T, c=1:C, i=1:I) - alpha * sum(z[i] for i=1:I))
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
    uDaily = readtable("Data/output/SARIMAdailyU.csv", header=true, makefactors=true)
    minWeekly, maxWeekly = uDaily[8,:MinVal], uDaily[8,:MaxVal]
    avgWeekly = (minWeekly + maxWeekly)/2
    dailyMin = []
    dailyMax = []
    for i=1:7
         push!(dailyMin, uDaily[i,:MinVal])
         push!(dailyMax, uDaily[i,:MaxVal])
    end
    ci = readtable("Data/output/ci.csv", header=true, makefactors=true)
    dt = readtable("Data/output/dt.csv", header=true, makefactors=true)
    dtci = readtable("Data/output/dtci.csv", header=true, makefactors=true)
    minVals = zeros(Float64, D,T,C,I)
    maxVals = zeros(Float64, D,T,C,I)
    for d in 1:D
        for t in 1:T
            for c in 1:C
                for i in 1:I
                    allComb = dtci[(dtci[:WeekDay] .== d) & (dtci[:StartTime] .== t) & (dtci[:Description] .== c) & (dtci[:Staff] .== i),:]
                    if nrow(allComb) > 0
                        minVals[d,t,c,i] = sum(allComb[:,:avgArrivals]) * dailyMin[d]
                        maxVals[d,t,c,i] = sum(allComb[:,:avgArrivals]) * dailyMax[d]
                    else
                        classInstructor = ci[(ci[:Description] .== c) & (ci[:Staff] .== i),:]
                        dayTime = dt[(dt[:WeekDay] .== d) & (dt[:StartTime] .== t),:]
                        if (nrow(classInstructor) > 0)
                            val = (sum(classInstructor[:,:avgArrivals]) + sum(dayTime[:,:avgArrivals]))/2.0
                            minVals[d,t,c,i] = val * dailyMin[d]
                            maxVals[d,t,c,i] = val * dailyMax[d]
                        else
                            minVals[d,t,c,i] = sum(dayTime[:,:avgArrivals]) * dailyMin[d]
                            maxVals[d,t,c,i] = sum(dayTime[:,:avgArrivals]) * dailyMax[d]
                        end
                    end
                end
            end
        end
    end
    return minVals, maxVals, minWeekly, maxWeekly, dailyMin, dailyMax
end
