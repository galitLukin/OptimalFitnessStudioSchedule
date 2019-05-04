using DataFrames, JuMP

function firstUncertainty()
    lastWeekSchedule = readtable("Data/output/attendanceLastWeekIndex.csv", header=true, makefactors=true)
    a = zeros(Int8, D,T,C,I)
    for k in 1:size(lastWeekSchedule, 1)
        d = lastWeekSchedule[k, :WeekDay]
        t = lastWeekSchedule[k, :StartTime]
        c = lastWeekSchedule[k, :Description]
        i = lastWeekSchedule[k, :Staff]
        a[d,t,c,i] = lastWeekSchedule[k, :Arrivals]
    end

    return a
end

function worstCase(x)
    # solve worst case min problem - formulate WC
    wc = Model(solver=GurobiSolver(OutputFlag=0))

    @variable(wc, A[1:D,1:T,1:C,1:I]>=0)
    @variable(wc, y)

    @objective(wc, Min, y)
    @constraint(wc, y >= sum(A[d,t,c,i]*x[d,t,c,i] for d=1:D, t=1:T, c=1:C, i=1:I))
    staticUncertainty(wc, A)

    solve(wc)

    aVals = getvalue(A)
    objective = getobjectivevalue(wc)
    return aVals, objective
end

function staticUncertainty(wc, A)
    u = readtable("Data/output/staticU.csv", header=true, makefactors=true)
    M = 500
    minVals = ones(Int64, D,T,C,I) * M
    maxVals = zeros(Int64, D,T,C,I)

    for k in 1:size(u, 1)
        d = Int8(u[k,:D])
        t = Int8(u[k,:T])
        c = Int8(u[k,:C])
        i = Int8(u[k,:I])
        mi = Int64(floor(u[k,:MinVal]))
        ma = Int64(floor(u[k,:MaxVal]))

        if t == 0 || c == 0 || i == 0
            continue
        end
        if mi < minVals[d,t,c,i]
            minVals[d,t,c,i] = mi
        end
        if ma > maxVals[d,t,c,i]
            maxVals[d,t,c,i] = ma
        end
    end

    maxDayVals = zeros(Int64, D)
    for d in 1:D
        slots = zeros(Int64, 28)
        for t in 1:T
            for c in 1:C
                for i in 1:I
                    if maxVals[d,t,c,i] > slots[t]
                        slots[t] = maxVals[d,t,c,i]
                    end
                end
            end
        end
        maxDayVals[d] = sum(slots)
    end

    for d in 1:D
        @constraint(wc, sum(A[d,t,c,i]*x[d,t,c,i] for t=1:T, c=1:C, i=1:I) <= maxDayVals[d] - 500)
        for t in 1:T
            for c in 1:C
                for i in 1:I
                    @constraint(wc, A[d,t,c,i] >= minVals[d,t,c,i])
                    @constraint(wc, A[d,t,c,i] <= maxVals[d,t,c,i])
                end
            end
        end
    end
end


function learnUncertainty()
    #learn best U from data
end
