-- MIT License; Copyright (c) 2026 HouseNimble contributors.
local M = {}
local state
local function finite(n) return type(n)=="number" and n==n and math.abs(n)<=1e12 end
local function say(ctx, da, en) return ctx.config.language=="en" and en or da end
local function text(ctx,id,value) ctx.ui.set_text(id,value) end
local function status(ctx,da,en) text(ctx,"status",say(ctx,da,en)) end
local function cancel(ctx)
  if state.pending and ctx.consumption then ctx.consumption.cancel(state.pending) end
  state.pending=nil
end
local function empty(ctx)
  if ctx.ui.pie_chart then
    ctx.ui.pie_chart({id="distribution",empty_text=say(ctx,"Ingen data for perioden","No data for this period"),slices={}})
  end
  text(ctx,"total","-- kWh"); text(ctx,"price","-- "..ctx.config.currency)
end
local function request(ctx)
  if not state.visible or state.pending or state.now<state.retry then return end
  if not ctx.consumption or not ctx.ui.pie_chart then
    status(ctx,"Kræver nyere core med Forbrugsfordeling","Requires a core with Consumption support");return
  end
  if not ctx.config.api_origin or ctx.config.api_origin=="" then
    status(ctx,"Angiv Home API-adressen i opsætningen","Set the Home API address in settings");return
  end
  state.sequence=state.sequence+1;state.tag="consumption:"..state.sequence
  state.pending=ctx.consumption.request({period=state.period,date=state.anchor,shift=state.shift,tag=state.tag})
  if state.pending then
    status(ctx,"Henter forbrug…","Loading consumption…")
  else
    state.retry=state.now+2000
    status(ctx,"Venter på forbindelse eller korrekt dato","Waiting for a connection or valid date")
  end
end
local function render(ctx,data)
  if type(data)~="table" or data.period~=state.period or type(data.from)~="string" or
    not data.from:match("^%d%d%d%d%-%d%d%-%d%d$") or type(data.to)~="string" or
    type(data.is_current)~="boolean" or type(data.groups)~="table" or #data.groups>32 then return false end
  local groups,total,positive,price,priced,negative={},0,0,0,true,0
  for _,g in ipairs(data.groups) do
    if type(g)~="table" or type(g.name)~="string" or #g.name==0 or #g.name>64 or
      g.name:find("%c") or not finite(g.kwh) or (g.price~=nil and not finite(g.price)) then return false end
    total=total+g.kwh;positive=positive+math.max(0,g.kwh);negative=negative+math.min(0,g.kwh)
    if g.price==nil then priced=false else price=price+g.price end
    groups[#groups+1]=g
  end
  if not finite(total) or not finite(price) or not finite(positive) then return false end
  table.sort(groups,function(a,b) if a.kwh==b.kwh then return a.name<b.name end return a.kwh>b.kwh end)
  local slices={}
  for _,g in ipairs(groups) do
    local share=positive>0 and 100*math.max(0,g.kwh)/positive or 0
    local cost=g.price~=nil and string.format("%.2f %s",g.price,ctx.config.currency) or "-- "..ctx.config.currency
    slices[#slices+1]={label=g.name,value=math.max(0,g.kwh),detail=string.format("%.2f kWh · %.1f%% · %s",g.kwh,share,cost)}
  end
  if not ctx.ui.pie_chart({id="distribution",empty_text=say(ctx,"Intet positivt forbrug","No positive consumption"),slices=slices}) then return false end
  text(ctx,"total",string.format("%.2f kWh",total))
  text(ctx,"price",priced and #groups>0 and string.format("%.2f %s",price,ctx.config.currency) or "-- "..ctx.config.currency)
  local date=data.from
  if state.period=="month" then date=date:sub(1,7) elseif state.period=="year" then date=date:sub(1,4) end
  text(ctx,"period",date)
  state.anchor=data.is_current and "current" or data.from;state.current=data.is_current;state.shift=0
  state.have=true;state.received=state.now;state.retry=state.now+ctx.config.refresh_seconds*1000
  if negative<0 then
    text(ctx,"status",say(ctx,"Negative korrektioner: ","Negative adjustments: ")..string.format("%.2f kWh",negative))
  elseif #groups==0 then status(ctx,"Ingen målinger for perioden","No readings for this period")
  else status(ctx,"Opdateret · data fra dit Home API","Updated · data from your Home API") end
  return true
end
function M.create(ctx)
  state={period="day",anchor="current",shift=0,current=true,visible=false,now=0,retry=0,sequence=0,have=false}
  ctx.ui.page({title=say(ctx,"Forbrugsfordeling","Consumption breakdown")})
  for _,row in ipairs({{"period","--"},{"total","-- kWh"},{"price","-- "..ctx.config.currency},{"status",say(ctx,"Venter på data","Waiting for data")}}) do
    ctx.ui.label({id=row[1],text=row[2]})
  end
  for _,b in ipairs({{"day","Dag","Day"},{"month","Måned","Month"},{"year","År","Year"},{"previous","Forrige","Previous"},{"next","Næste","Next"},{"current","Aktuel periode","Current period"},{"refresh","Opdater","Refresh"}}) do
    ctx.ui.button({id=b[1],text=say(ctx,b[2],b[3]),event=b[1]})
  end
  empty(ctx)
end
function M.show(ctx) state.visible=true;state.retry=0;request(ctx) end
function M.hide(ctx) state.visible=false;cancel(ctx) end
function M.destroy(ctx) M.hide(ctx) end
function M.event(ctx,event)
  if type(event)~="table" then return end
  if event.name=="tick" then
    if finite(event.now_ms) and event.now_ms>=state.now then state.now=event.now_ms end
    request(ctx);return
  end
  if event.name=="consumption" then
    if not state.visible or not state.pending or event.id~=state.pending or event.tag~=state.tag then return end
    state.pending=nil
    if finite(event.now_ms) and event.now_ms>=state.now then state.now=event.now_ms end
    if event.status~=200 or not render(ctx,event.json) then
      state.retry=state.now+math.max(10000,ctx.config.refresh_seconds*1000)
      status(ctx,state.have and "Kunne ikke opdatere · viser tidligere data" or "Ingen gyldige data fra Home API",state.have and "Update failed · showing earlier data" or "No valid Home API data")
    end
    return
  end
  if not state.visible then return end
  local action=event.name
  if action=="day" or action=="month" or action=="year" then
    if state.period==action then return end
    state.period=action;state.shift=0
  elseif action=="previous" or action=="next" then
    if action=="next" and state.current then return end
    if state.pending then return end
    state.shift=action=="previous" and -1 or 1
  elseif action=="current" then state.anchor="current";state.shift=0;state.current=true
  elseif action~="refresh" then return end
  cancel(ctx)
  if action~="refresh" then state.have=false;empty(ctx);text(ctx,"period","--") end
  state.retry=state.now;request(ctx)
end
return M
