#!/usr/bin/env python3
"""
Rent vs. Buy Financial Simulation
The Ohio State University - Fisher College of Business

Dependencies:  python3 -m pip install numpy numpy-financial matplotlib
Run:           python3 rent_vs_buy.py
"""

import tkinter as tk
from tkinter import ttk, font as tkfont, messagebox
import numpy as np
import numpy_financial as npf
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter
import matplotlib.colors as mcolors
import matplotlib.patches

SCARLET="#BB0000"; SCARLET_DK="#9B0000"; GRAY_OSU="#666666"
GRAY_DARK="#333333"; GRAY_MED="#4a4a4a"; GRAY_LIGHT="#999999"
WHITE="#FFFFFF"; OFF_WHITE="#F7F7F2"; CREAM="#EAEADE"
CARD_BG="#FFFFFF"; ENTRY_BG="#F2F2EC"; BORDER="#D0D0C8"
GREEN_OK="#2E7D32"; RED_WARN="#C62828"
CHART_FACE="#FAFAF5"; CHART_BG="#F2F2EC"

# ── Financial Engine ────────────────────────

def run_sim(p):
    hp=p["home_price"]; sq=p["sqft"]
    dp=p["down_pct"]/100; ra=p["mortgage_rate"]/100; ty=p["mortgage_term"]
    pt=p["prop_tax"]/100; ins=p["insurance"]; mt=p["maintenance"]/100
    ap=p["appreciation"]/100; cb=p["closing_buy"]/100; cs=p["closing_sell"]/100
    tx=p["marginal_tax"]/100; hy=p["hold_years"]
    mr=p["monthly_rent"]; rg=p["rent_growth"]/100; ri=p["renter_ins"]
    ir=p["invest_return"]/100; dr=p["discount_rate"]/100
    sal=p["annual_salary"]; stx=p["state_tax"]/100
    md=p["monthly_debt"]; ms=p["monthly_savings"]; ef=p["emergency_fund"]

    months=int(hy*12); rmo=ra/12; npmt=int(ty*12)
    down=hp*dp; loan=hp-down; closebuy=hp*cb
    if loan>0 and rmo>0: mpmt=npf.pmt(rmo,npmt,-loan)
    elif loan>0: mpmt=loan/npmt
    else: mpmt=0.0

    bcf=[0.0]*(months+1); bcf[0]=-(down+closebuy)
    bal=loan; ti=tpr=tins=tmt=0.0
    eq_ts=[0.0]; bmo=[]; hv_ts=[hp]
    for m in range(1,months+1):
        ip=bal*rmo if bal>0 else 0; pp=mpmt-ip if bal>0 else 0
        if pp>bal: pp=bal
        bal-=pp
        ptm=(hp*(1+ap)**((m-1)/12))*pt/12; im=ins/12
        mm=(hp*(1+ap)**((m-1)/12))*mt/12; tsh=ip*tx
        out=mpmt+ptm+im+mm-tsh; bcf[m]=-out
        ti+=ip; tpr+=ptm; tins+=im; tmt+=mm
        chv=hp*(1+ap)**(m/12); hv_ts.append(chv)
        eq_ts.append(chv-bal); bmo.append(out)

    fhv=hp*(1+ap)**hy; rembal=bal; csell=fhv*cs
    nsp=fhv-rembal-csell; bcf[months]+=nsp
    tbo=abs(sum(x for x in bcf if x<0))

    rcf=[0.0]*(months+1); trp=0.0; rmo_out=[]
    for m in range(1,months+1):
        yr=(m-1)//12; cr=mr*(1+rg)**yr; rim=ri/12
        out=cr+rim; rcf[m]=-out; trp+=cr; rmo_out.append(out)
    tro=abs(sum(x for x in rcf if x<0))

    irmo=ir/12; port=down+closebuy; port_ts=[port]
    for m in range(1,months+1):
        bo=abs(bcf[m]) if bcf[m]<0 else 0; ro=abs(rcf[m])
        d=bo-ro; port=port*(1+irmo)+max(d,0)
        if d<0: port+=d
        port_ts.append(max(port,0))
    rterm=max(port,0)

    dmo=dr/12; bnpv=npf.npv(dmo,bcf); rnpv=npf.npv(dmo,rcf)
    rnpvi=rnpv+rterm/(1+dmo)**months
    try:
        bi=npf.irr(bcf); birr=(1+bi)**12-1 if bi and not np.isnan(bi) else None
    except: birr=None
    ricf=[-(down+closebuy)]+[0.0]*months; ricf[-1]=rterm
    try:
        rii=npf.irr(ricf); rirr=(1+rii)**12-1 if rii and not np.isnan(rii) else None
    except: rirr=None

    bnet=nsp; rnet=rterm
    byavg=[]; ryavg=[]
    for y in range(int(hy)):
        s,e=y*12,min(y*12+12,months)
        byavg.append(np.mean(bmo[s:e])); ryavg.append(np.mean(rmo_out[s:e]))

    ftx=sal*tx; stax=sal*stx; mnet=(sal-ftx-stax)/12
    abm=np.mean(bmo[:12]) if bmo else 0
    arm=np.mean(rmo_out[:12]) if rmo_out else 0
    gmo=sal/12
    bhp=(abm/mnet*100) if mnet>0 else 0; rhp=(arm/mnet*100) if mnet>0 else 0
    bdti=((abm+md)/gmo*100) if gmo>0 else 0; rdti=((arm+md)/gmo*100) if gmo>0 else 0
    bleft=mnet-abm-md-ms; rleft=mnet-arm-md-ms
    bef=ef/abm if abm>0 else 0

    fint=(hp-down)*rmo; fprin=mpmt-fint if mpmt>fint else 0
    bpie={"Principal":fprin,"Interest":fint,"Prop Tax":hp*pt/12,
          "Insurance":ins/12,"Maint":hp*mt/12}
    cash_close=down+closebuy

    return {
        "months":months,"hold_years":hy,"sqft":sq,
        "down_payment":down,"loan_amount":loan,"monthly_pmt":mpmt,
        "total_interest":ti,"total_prop_tax":tpr,"total_insurance":tins,
        "total_maint":tmt,"future_home_value":fhv,
        "remaining_balance":rembal,"closing_sell_cost":csell,
        "net_sale_proceeds":nsp,"total_buy_outflows":tbo,
        "buy_npv":bnpv,"buy_irr":birr,"buyer_net_wealth":bnet,
        "total_rent_paid":trp,"total_rent_outflows":tro,"renter_terminal":rterm,
        "rent_npv":rnpv,"rent_npv_with_invest":rnpvi,
        "rent_irr":rirr,"renter_net_wealth":rnet,
        "advantage":"BUY" if bnet>rnet else "RENT",
        "advantage_amount":abs(bnet-rnet),
        "price_per_sqft":hp/sq if sq>0 else 0,
        "future_price_sqft":fhv/sq if sq>0 else 0,
        "equity_ts":eq_ts,"portfolio_ts":port_ts,"hv_ts":hv_ts,
        "buy_yearly":byavg,"rent_yearly":ryavg,
        "monthly_net":mnet,"avg_buy_mo":abm,"avg_rent_mo":arm,
        "buy_housing_pct":bhp,"rent_housing_pct":rhp,
        "buy_dti":bdti,"rent_dti":rdti,
        "buy_left":bleft,"rent_left":rleft,"buy_ef":bef,
        "buy_pie":bpie,"cash_to_close":cash_close,
    }

def quick_adv(p, hold=None, appr=None, rate=None):
    pc=dict(p)
    if hold is not None: pc["hold_years"]=hold
    if appr is not None: pc["appreciation"]=appr
    if rate is not None: pc["mortgage_rate"]=rate
    r=run_sim(pc); return r["buyer_net_wealth"]-r["renter_net_wealth"]

def find_breakeven(p, mx=30):
    for y in range(1,mx+1):
        if quick_adv(p,hold=y)>0: return y
    return None

def find_rent_eq(p):
    lo,hi=0,p["monthly_rent"]*4; pc=dict(p)
    for _ in range(40):
        mid=(lo+hi)/2; pc["monthly_rent"]=mid
        d=quick_adv(pc)
        if abs(d)<5: return mid
        if d>0: hi=mid
        else: lo=mid
    return (lo+hi)/2

def fmt_usd(v): return "N/A" if v is None else f"${v:,.0f}"
def fmt_usd2(v): return "N/A" if v is None else f"${v:,.2f}"
def fmt_pct(v): return "N/A" if v is None else f"{v*100:,.2f}%"
def usd_k(x,_): return f"${x:,.0f}K"
def usd_fmt(x,_): return f"${x:,.0f}"

# ── GUI ─────────────────────────────────────

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Rent vs. Buy  |  Fisher College of Business")
        self.configure(bg=OFF_WHITE)
        self.minsize(1400,850); self.geometry("1500x950")

        self.head_font=tkfont.Font(family="Georgia",size=14,weight="bold")
        self.big_font=tkfont.Font(family="Georgia",size=18,weight="bold")
        self.label_font=tkfont.Font(family="Helvetica Neue",size=12)
        self.entry_font=tkfont.Font(family="Menlo",size=12)
        self.result_font=tkfont.Font(family="Helvetica Neue",size=13)
        self.small_font=tkfont.Font(family="Helvetica Neue",size=11)
        self.mono_font=tkfont.Font(family="Menlo",size=13)
        self._build()

    def _build(self):
        # Header
        hdr=tk.Frame(self,bg=SCARLET,height=58); hdr.pack(fill="x"); hdr.pack_propagate(False)
        fl=tk.Frame(hdr,bg=SCARLET); fl.pack(side="left",padx=24,pady=6)
        tk.Label(fl,text="THE OHIO STATE UNIVERSITY",font=tkfont.Font(family="Georgia",size=9,weight="bold"),bg=SCARLET,fg=WHITE).pack(anchor="w")
        tk.Label(fl,text="Fisher College of Business",font=tkfont.Font(family="Georgia",size=14,weight="bold"),bg=SCARLET,fg=WHITE).pack(anchor="w")
        fr=tk.Frame(hdr,bg=SCARLET); fr.pack(side="right",padx=24,pady=6)
        tk.Label(fr,text="Rent vs. Buy Simulator",font=tkfont.Font(family="Georgia",size=16),bg=SCARLET,fg=WHITE).pack(anchor="e")
        tk.Label(fr,text="NPV | IRR | Opportunity Cost | Sensitivity",font=self.small_font,bg=SCARLET,fg="#FFCCCC").pack(anchor="e")
        tk.Frame(self,bg=GRAY_OSU,height=3).pack(fill="x")

        # ── PanedWindow: top inputs / bottom results ──
        self.paned=tk.PanedWindow(self,orient=tk.VERTICAL,bg=GRAY_OSU,
                                   sashwidth=6,sashrelief="raised",
                                   sashpad=2)
        self.paned.pack(fill="both",expand=True,padx=0,pady=0)

        # Top pane: inputs
        top_pane=tk.Frame(self.paned,bg=OFF_WHITE)
        self.paned.add(top_pane,minsize=180,height=290)

        tc=tk.Canvas(top_pane,bg=OFF_WHITE,highlightthickness=0)
        ts=tk.Scrollbar(top_pane,orient="horizontal",command=tc.xview)
        self.input_frame=tk.Frame(tc,bg=OFF_WHITE)
        self.input_frame.bind("<Configure>",lambda e:tc.configure(scrollregion=tc.bbox("all")))
        tc.create_window((0,0),window=self.input_frame,anchor="nw")
        tc.configure(xscrollcommand=ts.set)
        tc.pack(fill="both",expand=True,padx=16,pady=(8,0)); ts.pack(fill="x",padx=16)

        self.entries={}
        self._card(self.input_frame,"Subject Property",[
            ("home_price","Home Price ($)","400000"),("sqft","Square Footage","1800"),
            ("location","Location",""),],text_fields=["location"])
        self._card(self.input_frame,"Lifestyle & Budget",[
            ("annual_salary","Gross Salary ($/yr)","85000"),("state_tax","State Tax (%)","4.0"),
            ("monthly_debt","Other Debt ($/mo)","400"),("monthly_savings","Savings Goal ($/mo)","500"),
            ("emergency_fund","Emergency Fund ($)","15000"),])
        self._card(self.input_frame,"Purchase",[
            ("down_pct","Down Payment (%)","20"),("mortgage_rate","Mortgage Rate (%)","6.75"),
            ("mortgage_term","Loan Term (yrs)","30"),("prop_tax","Property Tax (%/yr)","1.25"),
            ("insurance","Home Ins. ($/yr)","1800"),("maintenance","Maintenance (%/yr)","1.0"),
            ("appreciation","Appreciation (%/yr)","3.0"),("closing_buy","Close Cost Buy (%)","3.0"),
            ("closing_sell","Close Cost Sell (%)","6.0"),])
        self._card(self.input_frame,"Renting",[
            ("monthly_rent","Monthly Rent ($)","2000"),("rent_growth","Rent Increase (%/yr)","3.0"),
            ("renter_ins","Renter Ins. ($/yr)","250"),])
        self._card(self.input_frame,"Analysis",[
            ("hold_years","Hold Period (yrs)","7"),("invest_return","Alt. Return (%/yr)","8.0"),
            ("discount_rate","Discount Rate (%/yr)","7.0"),("marginal_tax","Marginal Tax (%)","24"),])

        bf=tk.Frame(self.input_frame,bg=CARD_BG,highlightthickness=1,highlightbackground=BORDER,width=150)
        bf.pack(side="left",padx=6,anchor="n",fill="y"); bf.pack_propagate(False)
        tk.Button(bf,text="RUN\nSIMULATION",font=self.head_font,bg=SCARLET,fg=WHITE,
                  activebackground=SCARLET_DK,activeforeground=WHITE,bd=0,padx=14,pady=20,
                  cursor="hand2",command=self._run,wraplength=120,justify="center"
                  ).pack(expand=True,fill="both",padx=8,pady=8)

        # Bottom pane: tabbed results
        bot_pane=tk.Frame(self.paned,bg=OFF_WHITE)
        self.paned.add(bot_pane,minsize=300)

        style=ttk.Style(); style.theme_use("default")
        style.configure("OSU.TNotebook",background=OFF_WHITE,borderwidth=0)
        style.configure("OSU.TNotebook.Tab",background=CREAM,foreground=GRAY_DARK,
                        padding=[18,8],font=("Georgia",12,"bold"))
        style.map("OSU.TNotebook.Tab",background=[("selected",SCARLET)],foreground=[("selected",WHITE)])
        self.notebook=ttk.Notebook(bot_pane,style="OSU.TNotebook")
        self.notebook.pack(fill="both",expand=True,padx=16,pady=(8,12))

        self.tab_dash=tk.Frame(self.notebook,bg=OFF_WHITE)
        self.notebook.add(self.tab_dash,text="  Dashboard  ")
        self.tab_sens=tk.Frame(self.notebook,bg=OFF_WHITE)
        self.notebook.add(self.tab_sens,text="  Sensitivity  ")
        tab_det=tk.Frame(self.notebook,bg=OFF_WHITE)
        self.notebook.add(tab_det,text="  Detail  ")

        self.result_text=tk.Text(tab_det,bg=WHITE,fg=GRAY_DARK,font=self.result_font,
                                  relief="flat",padx=24,pady=18,wrap="word",state="disabled",
                                  insertbackground=GRAY_DARK,selectbackground=SCARLET,
                                  selectforeground=WHITE,highlightthickness=1,highlightbackground=BORDER)
        det_scroll=tk.Scrollbar(tab_det,command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=det_scroll.set)
        det_scroll.pack(side="right",fill="y")
        self.result_text.pack(fill="both",expand=True)
        for tag,kw in [("header",{"font":self.head_font,"foreground":SCARLET}),
            ("green",{"foreground":GREEN_OK}),("red",{"foreground":RED_WARN}),
            ("orange",{"foreground":"#E65100"}),
            ("sub",{"foreground":GRAY_LIGHT,"font":self.small_font}),
            ("explain",{"foreground":GRAY_MED,"font":self.result_font}),
            ("bold",{"font":tkfont.Font(family="Menlo",size=14,weight="bold"),"foreground":GRAY_DARK}),
            ("bigbold",{"font":tkfont.Font(family="Georgia",size=16,weight="bold"),"foreground":GRAY_DARK}),
            ("warn",{"foreground":RED_WARN,"font":self.result_font}),
            ("ok",{"foreground":GREEN_OK,"font":self.result_font}),
            ("kv",{"font":self.mono_font,"foreground":GRAY_DARK}),]:
            self.result_text.tag_configure(tag,**kw)

        self._placeholder()

    def _card(self,parent,title,fields,text_fields=None):
        text_fields=text_fields or []
        f=tk.Frame(parent,bg=CARD_BG,highlightthickness=1,highlightbackground=BORDER)
        f.pack(side="left",padx=5,anchor="n")
        tk.Frame(f,bg=SCARLET,height=4).pack(fill="x")
        tk.Label(f,text=title,font=tkfont.Font(family="Georgia",size=11,weight="bold"),
                 bg=CARD_BG,fg=SCARLET,padx=8,pady=4).pack(anchor="w")
        for key,label,default in fields:
            row=tk.Frame(f,bg=CARD_BG); row.pack(fill="x",padx=8,pady=1)
            tk.Label(row,text=label,font=tkfont.Font(family="Helvetica Neue",size=10),
                     bg=CARD_BG,fg=GRAY_DARK).pack(anchor="w")
            w=15 if key in text_fields else 10
            e=tk.Entry(row,font=tkfont.Font(family="Menlo",size=11),bg=ENTRY_BG,fg=GRAY_DARK,
                       insertbackground=GRAY_DARK,relief="flat",width=w,
                       highlightthickness=1,highlightcolor=SCARLET,highlightbackground=BORDER)
            e.insert(0,default); e.pack(anchor="w"); self.entries[key]=e
        tk.Frame(f,bg=CARD_BG,height=4).pack()

    def _placeholder(self):
        t=self.result_text; t.config(state="normal"); t.delete("1.0","end")
        t.insert("end","\n  Fill in the cards above and hit RUN SIMULATION.\n\n","sub")
        t.insert("end","  Drag the divider bar between inputs and results to resize.\n","sub")
        t.config(state="disabled")

    def _run(self):
        try:
            nk=[k for k in self.entries if k!="location"]
            p={k:float(self.entries[k].get().replace(",","")) for k in nk}
            p["location"]=self.entries["location"].get().strip()
        except ValueError:
            messagebox.showerror("Input Error","All numeric fields must be numbers."); return
        if p["hold_years"]<1 or p["hold_years"]>40:
            messagebox.showerror("Error","Hold period: 1-40 years."); return
        if p["sqft"]<=0:
            messagebox.showerror("Error","Square footage must be > 0."); return

        r=run_sim(p); be=find_breakeven(p); req=find_rent_eq(p)
        self._dashboard(r,p,be,req)
        self._sensitivity(r,p,be)
        self._detail(r,p,be,req)
        self.notebook.select(0)

    # ── DASHBOARD ───────────────────────────
    def _dashboard(self,r,p,be,req):
        for w in self.tab_dash.winfo_children(): w.destroy()

        winner=r["advantage"]; wc=GREEN_OK if winner=="BUY" else "#E65100"
        loser="RENT" if winner=="BUY" else "BUY"

        # Top banner: THE ANSWER
        banner=tk.Frame(self.tab_dash,bg=CARD_BG,highlightthickness=1,highlightbackground=BORDER)
        banner.pack(fill="x",padx=4,pady=(4,2))

        # Left: verdict
        vf=tk.Frame(banner,bg=CARD_BG); vf.pack(side="left",padx=20,pady=10)
        tk.Label(vf,text=f"YOU SHOULD {winner}.",font=tkfont.Font(family="Georgia",size=24,weight="bold"),
                 bg=CARD_BG,fg=wc).pack(anchor="w")
        tk.Label(vf,text=f"You'll have {fmt_usd(r['advantage_amount'])} MORE than if you {loser.lower()}.",
                 font=tkfont.Font(family="Helvetica Neue",size=14),bg=CARD_BG,fg=GRAY_DARK).pack(anchor="w")

        why = ""
        if winner == "BUY":
            why = (f"Your home grows from {fmt_usd(p['home_price'])} to "
                   f"{fmt_usd(r['future_home_value'])} in {r['hold_years']} years. "
                   f"After selling costs, you pocket {fmt_usd(r['net_sale_proceeds'])}. "
                   f"A renter investing the same capital would only reach "
                   f"{fmt_usd(r['renter_terminal'])}.")
        else:
            cap=r["down_payment"]+p["home_price"]*p["closing_buy"]/100
            why = (f"Investing {fmt_usd(cap)} instead of a down payment grows to "
                   f"{fmt_usd(r['renter_terminal'])} in {r['hold_years']} years. "
                   f"A buyer would only net {fmt_usd(r['net_sale_proceeds'])} "
                   f"after selling the home.")
        tk.Label(vf,text=why,font=tkfont.Font(family="Helvetica Neue",size=11),
                 bg=CARD_BG,fg=GRAY_MED,wraplength=600,justify="left").pack(anchor="w",pady=(4,0))

        # Right: key numbers
        nums=tk.Frame(banner,bg=CARD_BG); nums.pack(side="right",padx=20,pady=10)
        pairs = [
            ("Breakeven",f"Year {be}" if be else "Never",GREEN_OK if be and be<=r["hold_years"] else RED_WARN),
            ("Break-Even Rent",f"{fmt_usd(req)}/mo",GRAY_DARK),
            ("Cash to Buy",fmt_usd(r["cash_to_close"]),GRAY_DARK),
            ("Buy IRR",fmt_pct(r["buy_irr"]),GREEN_OK if r["buy_irr"] and r["buy_irr"]>0 else RED_WARN),
        ]
        for lbl,val,clr in pairs:
            row=tk.Frame(nums,bg=CARD_BG); row.pack(anchor="e",pady=1)
            tk.Label(row,text=lbl+"  ",font=self.small_font,bg=CARD_BG,fg=GRAY_LIGHT).pack(side="left")
            tk.Label(row,text=val,font=tkfont.Font(family="Menlo",size=13,weight="bold"),
                     bg=CARD_BG,fg=clr).pack(side="left")

        # Charts row
        fig=Figure(figsize=(14,3.8),dpi=100,facecolor=CHART_FACE)
        fig.subplots_adjust(left=0.06,right=0.97,top=0.88,bottom=0.15,wspace=0.32)

        # 1. Donut
        ax0=fig.add_subplot(1,3,1); ax0.set_facecolor(CHART_FACE)
        bp=r["buy_pie"]; labs=list(bp.keys()); sizes=list(bp.values())
        colors=[SCARLET,"#D44","#E88",GRAY_OSU,GRAY_LIGHT]
        if sum(sizes)>0:
            w1,t1,p1=ax0.pie(sizes,labels=labs,autopct="%1.0f%%",colors=colors[:len(sizes)],
                startangle=90,pctdistance=0.75,labeldistance=1.12,
                wedgeprops=dict(width=0.45,edgecolor=WHITE,linewidth=2),
                textprops={"fontsize":8,"color":GRAY_DARK})
            for t in p1: t.set_fontsize(7); t.set_color(GRAY_MED)
        ax0.set_title(f"Where Your {fmt_usd(sum(sizes))}/mo Goes (Buy)",
                      fontsize=10,fontweight="bold",color=GRAY_DARK,pad=8)

        # 2. Wealth
        ax1=fig.add_subplot(1,3,2); ax1.set_facecolor(WHITE)
        months=r["months"]; hold=int(r["hold_years"])
        ya=np.arange(0,months+1)/12
        ax1.fill_between(ya,[v/1000 for v in r["equity_ts"]],alpha=0.12,color=SCARLET)
        ax1.fill_between(ya,[v/1000 for v in r["portfolio_ts"]],alpha=0.10,color=GRAY_OSU)
        ax1.plot(ya,[v/1000 for v in r["equity_ts"]],color=SCARLET,lw=2.5,label="Buy: Equity")
        ax1.plot(ya,[v/1000 for v in r["portfolio_ts"]],color=GRAY_OSU,lw=2.5,label="Rent: Portfolio")
        bv=r["equity_ts"][-1]/1000; rv=r["portfolio_ts"][-1]/1000
        ax1.annotate(fmt_usd(r["buyer_net_wealth"]),xy=(hold,bv),fontsize=9,color=SCARLET,
                     fontweight="bold",xytext=(6,8),textcoords="offset points")
        ax1.annotate(fmt_usd(r["renter_terminal"]),xy=(hold,rv),fontsize=9,color=GRAY_OSU,
                     fontweight="bold",xytext=(6,-12),textcoords="offset points")
        if be and be<=hold:
            bm=be*12; ax1.axvline(be,color=SCARLET,ls=":",alpha=0.5,lw=1)
            ax1.annotate(f"Yr {be}",xy=(be,r["equity_ts"][bm]/1000),fontsize=8,color=SCARLET,
                         ha="center",xytext=(0,-20),textcoords="offset points",
                         arrowprops=dict(arrowstyle="->",color=SCARLET,lw=1))
        top_line = "The SCARLET line is what you keep if you BUY. The GRAY line is what you'd have if you RENT."
        ax1.set_title(top_line,fontsize=7.5,color=GRAY_MED,pad=8,style="italic")
        ax1.set_xlabel("Year",fontsize=9,color=GRAY_LIGHT)
        ax1.yaxis.set_major_formatter(FuncFormatter(usd_k))
        ax1.legend(fontsize=8,facecolor=WHITE,edgecolor=BORDER,labelcolor=GRAY_DARK,loc="upper left")
        ax1.tick_params(colors=GRAY_LIGHT,labelsize=8)
        ax1.grid(True,alpha=0.12,color=GRAY_LIGHT)
        ax1.spines["top"].set_visible(False); ax1.spines["right"].set_visible(False)
        for sp in ["bottom","left"]: ax1.spines[sp].set_color(BORDER)

        # 3. Monthly cost
        ax2=fig.add_subplot(1,3,3); ax2.set_facecolor(WHITE)
        yrs=np.arange(1,hold+1); w=0.35
        ax2.bar(yrs-w/2,r["buy_yearly"],w,color=SCARLET,alpha=0.85,label="Buy",edgecolor=WHITE,lw=0.5)
        ax2.bar(yrs+w/2,r["rent_yearly"],w,color=GRAY_OSU,alpha=0.85,label="Rent",edgecolor=WHITE,lw=0.5)
        ax2.set_title("What you pay each month, averaged by year.\nSCARLET = buy, GRAY = rent.",
                      fontsize=7.5,color=GRAY_MED,pad=8,style="italic")
        ax2.set_xlabel("Year",fontsize=9,color=GRAY_LIGHT)
        ax2.yaxis.set_major_formatter(FuncFormatter(usd_fmt))
        ax2.legend(fontsize=8,facecolor=WHITE,edgecolor=BORDER,labelcolor=GRAY_DARK)
        ax2.tick_params(colors=GRAY_LIGHT,labelsize=8); ax2.set_xticks(yrs)
        ax2.grid(True,axis="y",alpha=0.12,color=GRAY_LIGHT)
        ax2.spines["top"].set_visible(False); ax2.spines["right"].set_visible(False)
        for sp in ["bottom","left"]: ax2.spines[sp].set_color(BORDER)

        canvas=FigureCanvasTkAgg(fig,master=self.tab_dash)
        canvas.draw(); canvas.get_tk_widget().pack(fill="both",expand=True)

        # Affordability strip
        strip=tk.Frame(self.tab_dash,bg=CARD_BG,highlightthickness=1,highlightbackground=BORDER)
        strip.pack(fill="x",pady=(2,0))
        metrics=[
            ("Take-Home",fmt_usd(r["monthly_net"])+"/mo",GRAY_DARK,
             "Your monthly income after federal & state taxes."),
            ("Buy Cost",fmt_usd(r["avg_buy_mo"])+"/mo",SCARLET,
             "Average monthly ownership cost in year 1."),
            ("Rent Cost",fmt_usd(r["avg_rent_mo"])+"/mo",GRAY_OSU,
             "Monthly rent + renter's insurance."),
            ("Buy DTI",f"{r['buy_dti']:.0f}%",GREEN_OK if r["buy_dti"]<=36 else RED_WARN,
             "Must be under 36% to qualify for most loans."),
            ("Buy Leftover",fmt_usd(r["buy_left"])+"/mo",GREEN_OK if r["buy_left"]>0 else RED_WARN,
             "Cash left after housing, debt, and savings."),
            ("Emergency",f"{r['buy_ef']:.1f} mo",GREEN_OK if r["buy_ef"]>=3 else RED_WARN,
             "Months your emergency fund covers. Need 3-6."),
        ]
        for lbl,val,clr,tip in metrics:
            cell=tk.Frame(strip,bg=CARD_BG); cell.pack(side="left",expand=True,fill="both",padx=1)
            tk.Label(cell,text=lbl,font=tkfont.Font(family="Helvetica Neue",size=10),
                     bg=CARD_BG,fg=GRAY_LIGHT).pack(pady=(6,0))
            tk.Label(cell,text=val,font=tkfont.Font(family="Menlo",size=13,weight="bold"),
                     bg=CARD_BG,fg=clr).pack()
            tk.Label(cell,text=tip,font=tkfont.Font(family="Helvetica Neue",size=8),
                     bg=CARD_BG,fg=GRAY_LIGHT,wraplength=140).pack(pady=(0,6))

    # ── SENSITIVITY ─────────────────────────
    def _sensitivity(self,r,p,be):
        for w in self.tab_sens.winfo_children(): w.destroy()
        fig=Figure(figsize=(14,4.8),dpi=100,facecolor=CHART_FACE)
        fig.subplots_adjust(left=0.07,right=0.96,top=0.90,bottom=0.12,wspace=0.28)

        # 1. Heatmap
        ax1=fig.add_subplot(1,3,1)
        hrs=list(range(1,16)); ars=[0,1,2,3,4,5,6]
        grid=np.zeros((len(ars),len(hrs)))
        for ai,a in enumerate(ars):
            for hi,h in enumerate(hrs):
                grid[ai,hi]=quick_adv(p,hold=h,appr=a)/1000
        vm=max(abs(grid.min()),abs(grid.max()),1)
        cmap=mcolors.LinearSegmentedColormap.from_list("osu",[RED_WARN,WHITE,GREEN_OK])
        ax1.imshow(grid,cmap=cmap,aspect="auto",vmin=-vm,vmax=vm,origin="lower")
        ax1.set_xticks(range(len(hrs))); ax1.set_xticklabels(hrs,fontsize=7)
        ax1.set_yticks(range(len(ars))); ax1.set_yticklabels([f"{a}%" for a in ars],fontsize=8)
        ax1.set_xlabel("Hold Period (years)",fontsize=9,color=GRAY_DARK)
        ax1.set_ylabel("Appreciation (%/yr)",fontsize=9,color=GRAY_DARK)
        ax1.set_title("Buy Advantage ($K)\nGreen = Buy Wins, Red = Rent Wins",fontsize=10,fontweight="bold",color=GRAY_DARK,pad=6)
        for ai in range(len(ars)):
            for hi in range(len(hrs)):
                v=grid[ai,hi]; c=WHITE if abs(v)>vm*0.55 else GRAY_DARK
                ax1.text(hi,ai,f"{v:+.0f}",ha="center",va="center",fontsize=6,color=c,fontweight="bold")
        ch=int(p["hold_years"]); ca=int(p["appreciation"])
        if ch in hrs and ca in ars:
            ax1.add_patch(matplotlib.patches.Rectangle((hrs.index(ch)-0.5,ars.index(ca)-0.5),1,1,
                lw=2.5,edgecolor=SCARLET,facecolor="none"))
        ax1.tick_params(colors=GRAY_DARK,labelsize=7)

        # 2. Line by hold year
        ax2=fig.add_subplot(1,3,2); ax2.set_facecolor(WHITE)
        yl=list(range(1,21)); advs=[quick_adv(p,hold=y)/1000 for y in yl]
        ax2.fill_between(yl,advs,0,where=[a>=0 for a in advs],alpha=0.12,color=GREEN_OK,interpolate=True)
        ax2.fill_between(yl,advs,0,where=[a<0 for a in advs],alpha=0.12,color=RED_WARN,interpolate=True)
        ax2.plot(yl,advs,color=SCARLET,lw=2.5,marker="o",ms=3,mfc=SCARLET,mec=WHITE)
        ax2.axhline(0,color=GRAY_DARK,lw=1)
        if be and be<=20:
            ax2.axvline(be,color=GREEN_OK,ls="--",alpha=0.7)
            ax2.annotate(f"Breakeven Yr {be}",xy=(be,0),fontsize=9,color=GREEN_OK,fontweight="bold",
                         xytext=(8,18),textcoords="offset points",
                         arrowprops=dict(arrowstyle="->",color=GREEN_OK,lw=1.2))
        ax2.set_title("Above zero = buying wins.\nBelow zero = renting wins.",fontsize=9,color=GRAY_MED,pad=8,style="italic")
        ax2.set_xlabel("Hold Period (years)",fontsize=9,color=GRAY_LIGHT)
        ax2.set_ylabel("Buy Advantage ($K)",fontsize=9,color=GRAY_LIGHT)
        ax2.yaxis.set_major_formatter(FuncFormatter(lambda x,_:f"${x:+,.0f}K"))
        ax2.tick_params(colors=GRAY_LIGHT,labelsize=8)
        ax2.grid(True,alpha=0.12,color=GRAY_LIGHT)
        ax2.spines["top"].set_visible(False); ax2.spines["right"].set_visible(False)
        for sp in ["bottom","left"]: ax2.spines[sp].set_color(BORDER)

        # 3. By mortgage rate
        ax3=fig.add_subplot(1,3,3); ax3.set_facecolor(WHITE)
        rates=[4,4.5,5,5.5,6,6.5,7,7.5,8,8.5]
        ra=[quick_adv(p,rate=rt)/1000 for rt in rates]
        bc=[GREEN_OK if a>=0 else RED_WARN for a in ra]
        bars=ax3.bar(range(len(rates)),ra,color=bc,alpha=0.85,edgecolor=WHITE,lw=0.5)
        ax3.axhline(0,color=GRAY_DARK,lw=1)
        ax3.set_xticks(range(len(rates))); ax3.set_xticklabels([f"{r}%" for r in rates],fontsize=8)
        cr=p["mortgage_rate"]
        if cr in rates:
            idx=rates.index(cr); bars[idx].set_edgecolor(SCARLET); bars[idx].set_linewidth(2.5)
        ax3.set_title("How mortgage rate changes the verdict.\nYour rate is outlined.",fontsize=9,color=GRAY_MED,pad=8,style="italic")
        ax3.set_xlabel("Mortgage Rate",fontsize=9,color=GRAY_LIGHT)
        ax3.set_ylabel("Buy Advantage ($K)",fontsize=9,color=GRAY_LIGHT)
        ax3.yaxis.set_major_formatter(FuncFormatter(lambda x,_:f"${x:+,.0f}K"))
        ax3.tick_params(colors=GRAY_LIGHT,labelsize=8)
        ax3.grid(True,axis="y",alpha=0.12,color=GRAY_LIGHT)
        ax3.spines["top"].set_visible(False); ax3.spines["right"].set_visible(False)
        for sp in ["bottom","left"]: ax3.spines[sp].set_color(BORDER)

        canvas=FigureCanvasTkAgg(fig,master=self.tab_sens)
        canvas.draw(); canvas.get_tk_widget().pack(fill="both",expand=True)

        leg=tk.Frame(self.tab_sens,bg=CARD_BG,highlightthickness=1,highlightbackground=BORDER)
        leg.pack(fill="x",pady=(2,0))
        tk.Label(leg,text=f"Your current scenario: {p['mortgage_rate']}% rate, "
                 f"{int(p['hold_years'])} year hold, {p['appreciation']}% appreciation — "
                 f"highlighted with scarlet outline",
                 font=self.small_font,bg=CARD_BG,fg=GRAY_LIGHT).pack(pady=6)

    # ── DETAIL ──────────────────────────────
    def _detail(self,r,p,be,req):
        t=self.result_text; t.config(state="normal"); t.delete("1.0","end")
        def ln(text="",tag=None): t.insert("end",text+"\n",tag)
        def kv(l,v,tag=None): t.insert("end",f"  {l:<38}{v}\n",tag or "kv")

        sep="="*66; sep2="-"*66
        w=r["advantage"]; c="green" if w=="BUY" else "orange"
        loc=p.get("location",""); ls=f" in {loc}" if loc else ""

        # ── THE BOTTOM LINE ─────────────────
        ln(); ln(sep,"sub"); ln()
        ln(f"  THE BOTTOM LINE","header"); ln()
        ln(f"  You should {w}.","bigbold")
        ln()
        ln(f"  After {r['hold_years']} years{ls}, {w.lower()}ing leaves you","explain")
        ln(f"  {fmt_usd(r['advantage_amount'])} richer than the alternative.","explain")
        ln()

        if w=="BUY":
            ln("  Here's why:","header"); ln()
            ln(f"  • You buy a home for {fmt_usd(p['home_price'])}.","explain")
            ln(f"  • It appreciates at {p['appreciation']}%/yr to {fmt_usd(r['future_home_value'])}.","explain")
            ln(f"  • You sell it. After paying off the remaining","explain")
            ln(f"    {fmt_usd(r['remaining_balance'])} mortgage and {fmt_usd(r['closing_sell_cost'])}","explain")
            ln(f"    in selling costs, you walk away with","explain")
            ln(f"    {fmt_usd(r['net_sale_proceeds'])} cash.","green")
            ln()
            ln(f"  • Meanwhile, a renter who invested the same","explain")
            ln(f"    {fmt_usd(r['down_payment']+p['home_price']*p['closing_buy']/100)} in the market","explain")
            ln(f"    at {p['invest_return']}% would only have {fmt_usd(r['renter_terminal'])}.","explain")
            ln()
            ln(f"  • The difference: you're {fmt_usd(r['advantage_amount'])} ahead.","green")
        else:
            cap=r["down_payment"]+p["home_price"]*p["closing_buy"]/100
            ln("  Here's why:","header"); ln()
            ln(f"  • Instead of a {fmt_usd(r['down_payment'])} down payment","explain")
            ln(f"    + {fmt_usd(p['home_price']*p['closing_buy']/100)} closing costs,","explain")
            ln(f"    you invest {fmt_usd(cap)} in the market.","explain")
            ln(f"  • At {p['invest_return']}%/yr, it grows to {fmt_usd(r['renter_terminal'])}.","green")
            ln()
            ln(f"  • A buyer would only net {fmt_usd(r['net_sale_proceeds'])}","explain")
            ln(f"    after selling costs and mortgage payoff.","explain")
            ln()
            ln(f"  • The difference: you're {fmt_usd(r['advantage_amount'])} ahead.","green")

        ln(); ln(sep,"sub"); ln()

        # ── KEY NUMBERS ─────────────────────
        ln("  KEY NUMBERS YOU NEED TO KNOW","header"); ln()

        if be:
            kv("Breakeven Year",str(be),
               "green" if be<=r["hold_years"] else "orange")
            if be<=r["hold_years"]:
                ln(f"  Buying starts beating renting in year {be}.","ok")
                ln(f"  You plan to hold {r['hold_years']} years, so you're past it. Good.","ok")
            else:
                ln(f"  Buying doesn't beat renting until year {be}.","warn")
                ln(f"  You plan to hold {r['hold_years']} years. That's not enough time.","warn")
        else:
            kv("Breakeven Year","Never (30yr horizon)","red")
            ln("  Under these assumptions, buying never catches up.","warn")
        ln()

        kv("Break-Even Rent",f"{fmt_usd(req)}/mo")
        if req>p["monthly_rent"]:
            ln(f"  Your rent is {fmt_usd(p['monthly_rent'])}/mo, which is below the break-even.","explain")
            ln("  Renting is cheap enough that investing the savings wins.","explain")
        else:
            ln(f"  Your rent is {fmt_usd(p['monthly_rent'])}/mo, which is ABOVE the break-even.","explain")
            ln("  You're paying so much in rent that buying makes more sense.","explain")
        ln()

        kv("Cash Needed to Buy",fmt_usd(r["cash_to_close"]))
        ln(f"  Down payment: {fmt_usd(r['down_payment'])}  +  "
           f"Closing costs: {fmt_usd(p['home_price']*p['closing_buy']/100)}","explain")
        ln(f"  This is the check you write on closing day.","explain")

        ln(); ln(sep,"sub"); ln()

        # ── AFFORDABILITY ───────────────────
        ln("  CAN YOU ACTUALLY AFFORD THIS?","header"); ln()
        kv("Your Gross Salary",f"{fmt_usd(p['annual_salary'])}/yr")
        kv("Federal + State Taxes",f"{p['marginal_tax']}% + {p['state_tax']}%")
        kv("Monthly Take-Home",fmt_usd(r["monthly_net"]))
        ln()

        ln("  Monthly Housing Cost:","explain")
        kv("  If you BUY",f"{fmt_usd(r['avg_buy_mo'])}/mo  =  {r['buy_housing_pct']:.0f}% of take-home")
        kv("  If you RENT",f"{fmt_usd(r['avg_rent_mo'])}/mo  =  {r['rent_housing_pct']:.0f}% of take-home")
        ln()

        gm=p["annual_salary"]/12
        bhg=(r["avg_buy_mo"]/gm*100) if gm>0 else 0
        ln("  Lender Tests (will the bank approve you?):","header"); ln()

        kv("28% Rule: Housing / Gross Income",
           f"{bhg:.0f}%  {'PASS' if bhg<=28 else 'FAIL — over 28%'}",
           "ok" if bhg<=28 else "warn")
        if bhg>28:
            ln("  Your housing cost is too high relative to gross income.","warn")
            ln("  Most lenders will flag this. Consider a cheaper home.","warn")
        else:
            ln("  Your housing cost is within the standard lending limit.","ok")
        ln()

        kv("36% Rule: Total DTI",
           f"{r['buy_dti']:.0f}%  {'PASS' if r['buy_dti']<=36 else 'FAIL — over 36%'}",
           "ok" if r["buy_dti"]<=36 else "warn")
        if r["buy_dti"]>36:
            ln("  Housing + your other debts exceed the 36% limit.","warn")
            ln("  Pay down debt or increase income before buying.","warn")
        else:
            ln("  Total debt load is manageable by lender standards.","ok")
        ln()

        kv("Money Left Over After ALL Bills",
           f"{fmt_usd(r['buy_left'])}/mo","green" if r["buy_left"]>0 else "red")
        if r["buy_left"]<=0:
            ln("  You'd be living paycheck to paycheck. This is risky.","warn")
        elif r["buy_left"]<500:
            ln("  Tight but workable. Not much room for surprises.","orange")
        else:
            ln("  Comfortable cushion after all obligations.","ok")
        ln()

        kv("Emergency Fund Coverage",f"{r['buy_ef']:.1f} months of housing costs",
           "green" if r["buy_ef"]>=3 else "red")
        if r["buy_ef"]<3:
            ln("  Danger zone. You need at least 3 months of reserves.","warn")
            ln(f"  Recommended savings before buying: {fmt_usd(r['avg_buy_mo']*6)}","warn")
        elif r["buy_ef"]<6:
            ln("  Meets minimum. Aim for 6 months for true comfort.","explain")
        else:
            ln("  Strong reserves. You're well-prepared for surprises.","ok")

        ln(); ln(sep,"sub"); ln()

        # ── FULL BUY NUMBERS ────────────────
        ln("  FULL BUY BREAKDOWN","header"); ln()
        kv("Home Price",fmt_usd(p["home_price"]))
        kv("Square Footage",f"{p['sqft']:,.0f}")
        kv("Price per Sq Ft",fmt_usd2(r["price_per_sqft"]))
        kv("Down Payment",fmt_usd(r["down_payment"]))
        kv("Loan Amount",fmt_usd(r["loan_amount"]))
        kv("Monthly Mortgage Payment",fmt_usd(r["monthly_pmt"]))
        ln()
        ln(f"  Over {r['hold_years']} years you will pay:","explain")
        kv("Total Interest to the Bank",fmt_usd(r["total_interest"]),"red")
        kv("Total Property Taxes",fmt_usd(r["total_prop_tax"]))
        kv("Total Insurance",fmt_usd(r["total_insurance"]))
        kv("Total Maintenance",fmt_usd(r["total_maint"]))
        kv("TOTAL MONEY OUT THE DOOR",fmt_usd(r["total_buy_outflows"]),"red")
        ln()
        ln(f"  But when you sell:","explain")
        kv("Home Value at Sale",fmt_usd(r["future_home_value"]),"green")
        kv("Future $/Sq Ft",fmt_usd2(r["future_price_sqft"]))
        kv("Remaining Mortgage Balance",fmt_usd(r["remaining_balance"]))
        kv("Selling Costs (agent, fees)",fmt_usd(r["closing_sell_cost"]))
        kv("NET CASH YOU KEEP",fmt_usd(r["net_sale_proceeds"]),"green")
        ln()
        kv("NPV (today's dollars)",fmt_usd(r["buy_npv"]),
           "green" if r["buy_npv"]>0 else "red")
        kv("IRR (your annual return)",fmt_pct(r["buy_irr"]),
           "green" if r["buy_irr"] and r["buy_irr"]>0 else "red")
        if r["buy_irr"]:
            if r["buy_irr"]>p["discount_rate"]/100:
                ln(f"  Your return ({fmt_pct(r['buy_irr'])}) beats your hurdle rate ({p['discount_rate']}%).","ok")
                ln("  This means buying creates value for you.","ok")
            else:
                ln(f"  Your return ({fmt_pct(r['buy_irr'])}) is below your hurdle rate ({p['discount_rate']}%).","warn")
                ln("  Your money would work harder invested elsewhere.","warn")

        ln(); ln(sep2,"sub"); ln()

        # ── FULL RENT NUMBERS ───────────────
        ln("  FULL RENT BREAKDOWN","header"); ln()
        kv("Starting Monthly Rent",fmt_usd(p["monthly_rent"]))
        kv("Annual Rent Increase",f"{p['rent_growth']}%")
        kv(f"Rent in Year {r['hold_years']}",
           fmt_usd(p["monthly_rent"]*(1+p["rent_growth"]/100)**(r["hold_years"]-1)))
        kv("Total Rent Paid",fmt_usd(r["total_rent_paid"]),"red")
        ln()
        cap=r["down_payment"]+p["home_price"]*p["closing_buy"]/100
        ln(f"  Instead of buying, you invest {fmt_usd(cap)}:","explain")
        kv("Investment Return",f"{p['invest_return']}%/yr")
        kv("Portfolio After "+str(r["hold_years"])+" Years",fmt_usd(r["renter_terminal"]),"green")
        ln()
        kv("NPV (today's dollars)",fmt_usd(r["rent_npv_with_invest"]),
           "green" if r["rent_npv_with_invest"]>0 else "red")
        kv("IRR (your annual return)",fmt_pct(r["rent_irr"]),
           "green" if r["rent_irr"] and r["rent_irr"]>0 else "red")

        ln(); ln(sep2,"sub"); ln()

        # ── OPPORTUNITY COST ────────────────
        ln("  OPPORTUNITY COST","header"); ln()
        opp=r["renter_terminal"]-r["buyer_net_wealth"]
        if opp>0:
            ln(f"  By buying, you MISS OUT on {fmt_usd(abs(opp))}.","red")
            ln()
            ln("  That's the growth your money would have earned","explain")
            ln("  in the market if you'd rented instead. Every dollar","explain")
            ln("  in a house is a dollar that can't earn stock returns.","explain")
        else:
            ln(f"  By buying, you GAIN {fmt_usd(abs(opp))} over investing.","green")
            ln()
            ln("  Your home's appreciation and forced savings through","explain")
            ln("  mortgage payments outperform what the market would","explain")
            ln("  have returned on your invested down payment.","explain")

        ln(); ln(sep,"sub"); ln()

        # ── GLOSSARY ────────────────────────
        ln("  GLOSSARY — WHAT THESE TERMS MEAN","header"); ln()
        terms=[
            ("NPV (Net Present Value)","A dollar today is worth more than a dollar next year. NPV converts all future costs and gains into today's dollars. Positive = you come out ahead."),
            ("IRR (Internal Rate of Return)","The annual return your money effectively earns. If IRR is higher than your discount rate ("+f"{p['discount_rate']}%"+"), the decision creates wealth."),
            ("Opportunity Cost","What you sacrifice by picking one option. If you put $80K into a house, that $80K can't also be earning stock market returns."),
            ("Breakeven Year","The first year where buying becomes cheaper than renting. If you sell before this year, renting would have been smarter."),
            ("Break-Even Rent","The monthly rent that makes renting and buying produce identical wealth. If your actual rent is below this, renting wins."),
            ("28/36 Rule","A lending guideline. Housing should be under 28% of gross income. Total debt payments should be under 36% of gross income."),
            ("DTI (Debt-to-Income)","Monthly debt payments divided by monthly gross income. Includes housing, car, student loans, and credit cards."),
            ("Appreciation","How much the home's value increases each year, expressed as a percentage."),
            ("Equity","The portion of the home you actually own — home value minus remaining mortgage."),
        ]
        for term,desc in terms:
            ln(f"  {term}","orange")
            ln(f"  {desc}","explain")
            ln()

        t.config(state="disabled"); t.see("1.0")

if __name__=="__main__":
    App().mainloop()