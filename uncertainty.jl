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

    @variable(model, A[1:D,1:T,1:C,1:I]>=0)
    @variable(model, y)

    @objective(model, Max, y)
    @constraint(model, y <= sum(A[d,t,c,i]*x[d,t,c,i] for d=1:D, t=1:T, c=1:C, i=1:I))

end

function staticUncertainty()
    u = readtable("Data/output/staticU.csv", header=true, makefactors=true)

end


function learnUncertainty()
    #learn best U from data
end
