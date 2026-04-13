#!/usr/bin/env python3
"""
Rent vs. Buy Financial Simulation
NPV / IRR / Opportunity-Cost / Lifestyle Analysis

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

# ──────────────────────────────────────────────
# Ohio State Buckeyes palette
# ──────────────────────────────────────────────
SCARLET     = "#BB0000"
SCARLET_DK  = "#9B0000"
GRAY_OSU    = "#666666"
GRAY_DARK   = "#333333"
GRAY_MED    = "#4a4a4a"
GRAY_LIGHT  = "#999999"
WHITE       = "#FFFFFF"
OFF_WHITE   = "#F7F7F2"
CREAM       = "#EAEADE"
CARD_BG     = "#FFFFFF"
ENTRY_BG    = "#F2F2EC"
BORDER      = "#D0D0C8"
GREEN_OK    = "#2E7D32"
RED_WARN    = "#C62828"
CHART_FACE  = "#FAFAF5"
CHART_BG    = "#F2F2EC"

# ──────────────────────────────────────────────
# Financial engine
# ──────────────────────────────────────────────

def run_simulation(p):
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
    equity_ts=[0.0]; bmo_out=[]; hv_ts=[hp]

    for m in range(1,months+1):
        ip=bal*rmo if bal>0 else 0; pp=mpmt-ip if bal>0 else 0
        if pp>bal: pp=bal
        bal-=pp
        ptm=(hp*(1+ap)**((m-1)/12))*pt/12; im=ins/12
        mm=(hp*(1+ap)**((m-1)/12))*mt/12; tsh=ip*tx
        out=mpmt+ptm+im+mm-tsh; bcf[m]=-out
        ti+=ip; tpr+=ptm; tins+=im; tmt+=mm
        chv=hp*(1+ap)**(m/12); hv_ts.append(chv)
        equity_ts.append(chv-bal); bmo_out.append(out)

    fhv=hp*(1+ap)**hy; rembal=bal; closesell=fhv*cs
    nsp=fhv-rembal-closesell; bcf[months]+=nsp
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

    dmo=dr/12
    bnpv=npf.npv(dmo,bcf); rnpv=npf.npv(dmo,rcf)
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
        byavg.append(np.mean(bmo_out[s:e])); ryavg.append(np.mean(rmo_out[s:e]))

    # Lifestyle
    ftx=sal*tx; stax=sal*stx; mnet=(sal-ftx-stax)/12
    abm=np.mean(bmo_out[:12]) if bmo_out else 0
    arm=np.mean(rmo_out[:12]) if rmo_out else 0
    gmo=sal/12
    bhp=(abm/mnet*100) if mnet>0 else 0; rhp=(arm/mnet*100) if mnet>0 else 0
    bdti=((abm+md)/gmo*100) if gmo>0 else 0; rdti=((arm+md)/gmo*100) if gmo>0 else 0
    bleft=mnet-abm-md-ms; rleft=mnet-arm-md-ms
    bef=ef/abm if abm>0 else 0; ref=ef/arm if arm>0 else 0

    fint=(hp-down)*rmo; fprin=mpmt-fint if mpmt>fint else 0
    bpie={"Principal":fprin,"Interest":fint,"Prop Tax":hp*pt/12,
          "Insurance":ins/12,"Maint":hp*mt/12}
    rpie={"Rent":mr,"Renter Ins":ri/12}

    return {
        "months":months,"hold_years":hy,"sqft":sq,
        "down_payment":down,"loan_amount":loan,"monthly_pmt":mpmt,
        "total_interest":ti,"total_prop_tax":tpr,"total_insurance":tins,
        "total_maint":tmt,"future_home_value":fhv,
        "remaining_balance":rembal,"closing_sell_cost":closesell,
        "net_sale_proceeds":nsp,"total_buy_outflows":tbo,
        "buy_npv":bnpv,"buy_irr":birr,"buyer_net_wealth":bnet,
        "total_rent_paid":trp,"total_rent_outflows":tro,"renter_terminal":rterm,
        "rent_npv":rnpv,"rent_npv_with_invest":rnpvi,
        "rent_irr":rirr,"renter_net_wealth":rnet,
        "advantage":"BUY" if bnet>rnet else "RENT",
        "advantage_amount":abs(bnet-rnet),
        "price_per_sqft":hp/sq if sq>0 else 0,
        "future_price_sqft":fhv/sq if sq>0 else 0,
        "equity_ts":equity_ts,"portfolio_ts":port_ts,"hv_ts":hv_ts,
        "buy_yearly":byavg,"rent_yearly":ryavg,
        "monthly_net":mnet,"avg_buy_mo":abm,"avg_rent_mo":arm,
        "buy_housing_pct":bhp,"rent_housing_pct":rhp,
        "buy_dti":bdti,"rent_dti":rdti,
        "buy_left":bleft,"rent_left":rleft,
        "buy_ef":bef,"rent_ef":ref,
        "buy_pie":bpie,"rent_pie":rpie,
    }

def fmt_usd(v):  return "N/A" if v is None else f"${v:,.0f}"
def fmt_usd2(v): return "N/A" if v is None else f"${v:,.2f}"
def fmt_pct(v):  return "N/A" if v is None else f"{v*100:,.2f}%"
def usd_k(x,_):  return f"${x:,.0f}K" if x>=1 else f"${x*1000:,.0f}"
def usd_fmt(x,_): return f"${x:,.0f}"


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Rent vs. Buy  |  Fisher College of Business")
        self.configure(bg=OFF_WHITE)
        self.minsize(1400,850)
        self.geometry("1500x900")

        self.head_font   = tkfont.Font(family="Georgia",size=14,weight="bold")
        self.label_font  = tkfont.Font(family="Helvetica Neue",size=12)
        self.entry_font  = tkfont.Font(family="Menlo",size=12)
        self.result_font = tkfont.Font(family="Helvetica Neue",size=13)
        self.small_font  = tkfont.Font(family="Helvetica Neue",size=11)
        self.mono_font   = tkfont.Font(family="Menlo",size=13)

        self._build_ui()

    def _build_ui(self):
        # ── Scarlet header ──────────────────
        hdr=tk.Frame(self,bg=SCARLET,height=64); hdr.pack(fill="x"); hdr.pack_propagate(False)
        fl=tk.Frame(hdr,bg=SCARLET); fl.pack(side="left",padx=24,pady=8)
        tk.Label(fl,text="THE OHIO STATE UNIVERSITY",
                 font=tkfont.Font(family="Georgia",size=9,weight="bold"),
                 bg=SCARLET,fg=WHITE).pack(anchor="w")
        tk.Label(fl,text="Fisher College of Business",
                 font=tkfont.Font(family="Georgia",size=15,weight="bold"),
                 bg=SCARLET,fg=WHITE).pack(anchor="w")
        fr=tk.Frame(hdr,bg=SCARLET); fr.pack(side="right",padx=24,pady=8)
        tk.Label(fr,text="Rent vs. Buy Simulator",
                 font=tkfont.Font(family="Georgia",size=17),
                 bg=SCARLET,fg=WHITE).pack(anchor="e")
        tk.Label(fr,text="NPV  |  IRR  |  Opportunity Cost  |  Lifestyle",
                 font=self.small_font,bg=SCARLET,fg="#FFCCCC").pack(anchor="e")
        tk.Frame(self,bg=GRAY_OSU,height=3).pack(fill="x")

        # ── Top row: inputs scroll horizontally across ──
        top=tk.Frame(self,bg=OFF_WHITE)
        top.pack(fill="x",padx=16,pady=(10,4))

        tc=tk.Canvas(top,bg=OFF_WHITE,highlightthickness=0,height=280)
        ts=tk.Scrollbar(top,orient="horizontal",command=tc.xview)
        self.input_frame=tk.Frame(tc,bg=OFF_WHITE)
        self.input_frame.bind("<Configure>",lambda e:tc.configure(scrollregion=tc.bbox("all")))
        tc.create_window((0,0),window=self.input_frame,anchor="nw")
        tc.configure(xscrollcommand=ts.set)
        tc.pack(fill="x",expand=True); ts.pack(fill="x")

        self.entries={}

        self._card(self.input_frame,"Subject Property",[
            ("home_price","Home Price ($)","400000"),
            ("sqft","Square Footage","1800"),
            ("location","Location",""),
        ],text_fields=["location"])

        self._card(self.input_frame,"Lifestyle & Budget",[
            ("annual_salary","Gross Salary ($/yr)","85000"),
            ("state_tax","State Tax (%)","4.0"),
            ("monthly_debt","Other Debt ($/mo)","400"),
            ("monthly_savings","Savings Goal ($/mo)","500"),
            ("emergency_fund","Emergency Fund ($)","15000"),
        ])

        self._card(self.input_frame,"Purchase",[
            ("down_pct","Down Payment (%)","20"),
            ("mortgage_rate","Mortgage Rate (%)","6.75"),
            ("mortgage_term","Loan Term (yrs)","30"),
            ("prop_tax","Property Tax (%/yr)","1.25"),
            ("insurance","Home Ins. ($/yr)","1800"),
            ("maintenance","Maintenance (%/yr)","1.0"),
            ("appreciation","Appreciation (%/yr)","3.0"),
            ("closing_buy","Close Cost Buy (%)","3.0"),
            ("closing_sell","Close Cost Sell (%)","6.0"),
        ])

        self._card(self.input_frame,"Renting",[
            ("monthly_rent","Monthly Rent ($)","2000"),
            ("rent_growth","Rent Increase (%/yr)","3.0"),
            ("renter_ins","Renter Ins. ($/yr)","250"),
        ])

        self._card(self.input_frame,"Analysis",[
            ("hold_years","Hold Period (yrs)","7"),
            ("invest_return","Alt. Return (%/yr)","8.0"),
            ("discount_rate","Discount Rate (%/yr)","7.0"),
            ("marginal_tax","Marginal Tax (%)","24"),
        ])

        # Run button in a card
        btn_frame=tk.Frame(self.input_frame,bg=CARD_BG,highlightthickness=1,
                           highlightbackground=BORDER,width=160,height=270)
        btn_frame.pack(side="left",padx=6,anchor="n")
        btn_frame.pack_propagate(False)
        tk.Button(btn_frame,text="RUN\nSIMULATION",font=self.head_font,
                  bg=SCARLET,fg=WHITE,activebackground=SCARLET_DK,
                  activeforeground=WHITE,bd=0,padx=16,pady=30,
                  cursor="hand2",command=self._run,wraplength=120,
                  justify="center").pack(expand=True,fill="both",padx=10,pady=10)

        # ── Bottom: results area ────────────
        bottom=tk.Frame(self,bg=OFF_WHITE)
        bottom.pack(fill="both",expand=True,padx=16,pady=(4,12))

        style=ttk.Style(); style.theme_use("default")
        style.configure("OSU.TNotebook",background=OFF_WHITE,borderwidth=0)
        style.configure("OSU.TNotebook.Tab",background=CREAM,foreground=GRAY_DARK,
                        padding=[18,8],font=("Georgia",12,"bold"))
        style.map("OSU.TNotebook.Tab",background=[("selected",SCARLET)],
                  foreground=[("selected",WHITE)])

        self.notebook=ttk.Notebook(bottom,style="OSU.TNotebook")
        self.notebook.pack(fill="both",expand=True)

        # Tab 1: Dashboard (charts + verdict)
        self.tab_dash=tk.Frame(self.notebook,bg=OFF_WHITE)
        self.notebook.add(self.tab_dash,text="  Dashboard  ")

        # Tab 2: Detail
        tab_detail=tk.Frame(self.notebook,bg=OFF_WHITE)
        self.notebook.add(tab_detail,text="  Detail  ")
        self.result_text=tk.Text(tab_detail,bg=WHITE,fg=GRAY_DARK,
                                  font=self.result_font,relief="flat",
                                  padx=24,pady=18,wrap="word",state="disabled",
                                  insertbackground=GRAY_DARK,selectbackground=SCARLET,
                                  selectforeground=WHITE,highlightthickness=1,
                                  highlightbackground=BORDER)
        self.result_text.pack(fill="both",expand=True)
        for tag,kw in [
            ("header",{"font":self.head_font,"foreground":SCARLET}),
            ("green",{"foreground":GREEN_OK}),("red",{"foreground":RED_WARN}),
            ("orange",{"foreground":"#E65100"}),
            ("sub",{"foreground":GRAY_LIGHT,"font":self.small_font}),
            ("explain",{"foreground":GRAY_MED,"font":self.result_font}),
            ("bold",{"font":tkfont.Font(family="Menlo",size=14,weight="bold"),"foreground":GRAY_DARK}),
            ("warn",{"foreground":RED_WARN,"font":self.result_font}),
            ("ok",{"foreground":GREEN_OK,"font":self.result_font}),
            ("kv",{"font":self.mono_font,"foreground":GRAY_DARK}),
        ]:
            self.result_text.tag_configure(tag,**kw)

        self._show_placeholder()

    def _card(self,parent,title,fields,text_fields=None):
        text_fields=text_fields or []
        frame=tk.Frame(parent,bg=CARD_BG,highlightthickness=1,
                       highlightbackground=BORDER)
        frame.pack(side="left",padx=6,anchor="n")

        # Scarlet top bar
        tk.Frame(frame,bg=SCARLET,height=4).pack(fill="x")
        tk.Label(frame,text=title,font=tkfont.Font(family="Georgia",size=12,weight="bold"),
                 bg=CARD_BG,fg=SCARLET,anchor="w",padx=10,pady=6).pack(anchor="w")

        for key,label,default in fields:
            row=tk.Frame(frame,bg=CARD_BG)
            row.pack(fill="x",padx=10,pady=2)
            tk.Label(row,text=label,font=self.small_font,
                     bg=CARD_BG,fg=GRAY_DARK,anchor="w").pack(anchor="w")
            w=16 if key in text_fields else 11
            e=tk.Entry(row,font=self.entry_font,bg=ENTRY_BG,fg=GRAY_DARK,
                       insertbackground=GRAY_DARK,relief="flat",width=w,
                       highlightthickness=1,highlightcolor=SCARLET,
                       highlightbackground=BORDER)
            e.insert(0,default); e.pack(anchor="w",pady=(0,2))
            self.entries[key]=e
        tk.Frame(frame,bg=CARD_BG,height=6).pack()

    def _show_placeholder(self):
        t=self.result_text; t.config(state="normal"); t.delete("1.0","end")
        t.insert("end","\n  Fill in the cards above and hit RUN SIMULATION.\n\n","sub")
        t.insert("end","  Dashboard tab: visual verdict, charts & affordability.\n","sub")
        t.insert("end","  Detail tab: full financial breakdown with explanations.\n","sub")
        t.config(state="disabled")

    def _run(self):
        try:
            nk=[k for k in self.entries if k!="location"]
            p={k:float(self.entries[k].get().replace(",","")) for k in nk}
            p["location"]=self.entries["location"].get().strip()
        except ValueError:
            messagebox.showerror("Input Error","All numeric fields must be numbers."); return
        if p["hold_years"]<1 or p["hold_years"]>40:
            messagebox.showerror("Input Error","Hold period: 1-40 years."); return
        if p["sqft"]<=0:
            messagebox.showerror("Input Error","Square footage must be > 0."); return

        r=run_simulation(p)
        self._draw_dashboard(r,p)
        self._display_detail(r,p)
        self.notebook.select(0)

    # ── Dashboard ───────────────────────────
    def _draw_dashboard(self,r,p):
        for w in self.tab_dash.winfo_children(): w.destroy()

        fig=Figure(figsize=(14,5.2),dpi=100,facecolor=CHART_FACE)
        fig.subplots_adjust(left=0.06,right=0.97,top=0.88,bottom=0.12,wspace=0.35)

        winner=r["advantage"]; wc=GREEN_OK if winner=="BUY" else "#E65100"

        # ── 1. Verdict + Pie (left) ─────────
        ax0=fig.add_subplot(1,3,1); ax0.set_facecolor(CHART_FACE)
        ax0.axis("off")

        ax0.text(0.5,0.98,f"VERDICT: {winner}",transform=ax0.transAxes,
                 fontsize=20,fontweight="bold",color=wc,ha="center",va="top")
        ax0.text(0.5,0.88,f"saves {fmt_usd(r['advantage_amount'])} over {r['hold_years']} yrs",
                 transform=ax0.transAxes,fontsize=12,color=GRAY_MED,ha="center",va="top")

        # Donut: buy cost breakdown
        bp=r["buy_pie"]; labs=list(bp.keys()); sizes=list(bp.values())
        colors=[SCARLET,"#D44","#E88",GRAY_OSU,GRAY_LIGHT]
        if sum(sizes)>0:
            inner_ax=fig.add_axes([0.04,0.02,0.28,0.55])
            inner_ax.set_facecolor(CHART_FACE)
            wedges,txts,pcts=inner_ax.pie(sizes,labels=labs,autopct="%1.0f%%",
                colors=colors[:len(sizes)],startangle=90,pctdistance=0.78,
                labeldistance=1.15,wedgeprops=dict(width=0.45,edgecolor=WHITE,linewidth=2),
                textprops={"fontsize":8,"color":GRAY_DARK})
            for t in pcts: t.set_fontsize(7); t.set_color(GRAY_MED)
            inner_ax.set_title(f"Monthly Buy Cost: {fmt_usd(sum(sizes))}",
                              fontsize=10,color=GRAY_DARK,pad=6)

        # ── 2. Wealth over time (center) ────
        ax1=fig.add_subplot(1,3,2); ax1.set_facecolor(WHITE)
        months=r["months"]; hold=int(r["hold_years"])
        ya=np.arange(0,months+1)/12

        ax1.fill_between(ya,[v/1000 for v in r["equity_ts"]],alpha=0.15,color=SCARLET)
        ax1.fill_between(ya,[v/1000 for v in r["portfolio_ts"]],alpha=0.12,color=GRAY_OSU)
        ax1.plot(ya,[v/1000 for v in r["equity_ts"]],color=SCARLET,linewidth=2.5,label="Buy: Equity")
        ax1.plot(ya,[v/1000 for v in r["portfolio_ts"]],color=GRAY_OSU,linewidth=2.5,label="Rent: Portfolio")

        # End labels
        bval=r["equity_ts"][-1]/1000; rval=r["portfolio_ts"][-1]/1000
        ax1.annotate(fmt_usd(r["buyer_net_wealth"]),xy=(hold,bval),fontsize=10,
                     color=SCARLET,fontweight="bold",xytext=(6,8),textcoords="offset points")
        ax1.annotate(fmt_usd(r["renter_terminal"]),xy=(hold,rval),fontsize=10,
                     color=GRAY_OSU,fontweight="bold",xytext=(6,-12),textcoords="offset points")

        ax1.set_title("Wealth Over Time",fontsize=13,fontweight="bold",color=GRAY_DARK,pad=10)
        ax1.set_xlabel("Year",fontsize=10,color=GRAY_LIGHT)
        ax1.yaxis.set_major_formatter(FuncFormatter(usd_k))
        ax1.legend(fontsize=9,facecolor=WHITE,edgecolor=BORDER,labelcolor=GRAY_DARK,loc="upper left")
        ax1.tick_params(colors=GRAY_LIGHT,labelsize=9)
        ax1.grid(True,alpha=0.15,color=GRAY_LIGHT)
        ax1.spines["top"].set_visible(False); ax1.spines["right"].set_visible(False)
        for sp in ["bottom","left"]: ax1.spines[sp].set_color(BORDER)

        # ── 3. Monthly cost bars (right) ────
        ax2=fig.add_subplot(1,3,3); ax2.set_facecolor(WHITE)
        yrs=np.arange(1,hold+1); w=0.35
        ax2.bar(yrs-w/2,r["buy_yearly"],w,color=SCARLET,alpha=0.85,label="Buy",
                edgecolor=WHITE,linewidth=0.5)
        ax2.bar(yrs+w/2,r["rent_yearly"],w,color=GRAY_OSU,alpha=0.85,label="Rent",
                edgecolor=WHITE,linewidth=0.5)

        # Crossover annotation
        for i in range(len(yrs)-1):
            if r["buy_yearly"][i]>r["rent_yearly"][i] and r["buy_yearly"][i+1]<=r["rent_yearly"][i+1]:
                ax2.annotate("Crossover",xy=(yrs[i+1],r["rent_yearly"][i+1]),fontsize=8,
                             color=SCARLET,fontweight="bold",xytext=(0,12),
                             textcoords="offset points",ha="center",
                             arrowprops=dict(arrowstyle="->",color=SCARLET,lw=1.2))
                break
            elif r["rent_yearly"][i]>r["buy_yearly"][i] and r["rent_yearly"][i+1]<=r["buy_yearly"][i+1]:
                ax2.annotate("Crossover",xy=(yrs[i+1],r["buy_yearly"][i+1]),fontsize=8,
                             color=SCARLET,fontweight="bold",xytext=(0,12),
                             textcoords="offset points",ha="center",
                             arrowprops=dict(arrowstyle="->",color=SCARLET,lw=1.2))
                break

        ax2.set_title("Avg Monthly Cost by Year",fontsize=13,fontweight="bold",color=GRAY_DARK,pad=10)
        ax2.set_xlabel("Year",fontsize=10,color=GRAY_LIGHT)
        ax2.yaxis.set_major_formatter(FuncFormatter(usd_fmt))
        ax2.legend(fontsize=9,facecolor=WHITE,edgecolor=BORDER,labelcolor=GRAY_DARK)
        ax2.tick_params(colors=GRAY_LIGHT,labelsize=9)
        ax2.set_xticks(yrs)
        ax2.grid(True,axis="y",alpha=0.15,color=GRAY_LIGHT)
        ax2.spines["top"].set_visible(False); ax2.spines["right"].set_visible(False)
        for sp in ["bottom","left"]: ax2.spines[sp].set_color(BORDER)

        canvas=FigureCanvasTkAgg(fig,master=self.tab_dash)
        canvas.draw(); canvas.get_tk_widget().pack(fill="both",expand=True,side="top")

        # ── Affordability strip below charts ──
        strip=tk.Frame(self.tab_dash,bg=CARD_BG,highlightthickness=1,
                       highlightbackground=BORDER)
        strip.pack(fill="x",padx=0,pady=(4,0))

        metrics=[
            ("Take-Home Pay",fmt_usd(r["monthly_net"])+"/mo",GRAY_DARK),
            ("Buy Housing %",f"{r['buy_housing_pct']:.0f}% of net",
             GREEN_OK if r["buy_housing_pct"]<35 else RED_WARN),
            ("Buy DTI",f"{r['buy_dti']:.0f}%",GREEN_OK if r["buy_dti"]<=36 else RED_WARN),
            ("Rent DTI",f"{r['rent_dti']:.0f}%",GREEN_OK if r["rent_dti"]<=36 else RED_WARN),
            ("Buy Leftover",fmt_usd(r["buy_left"])+"/mo",GREEN_OK if r["buy_left"]>0 else RED_WARN),
            ("Rent Leftover",fmt_usd(r["rent_left"])+"/mo",GREEN_OK if r["rent_left"]>0 else RED_WARN),
            ("Emergency",f"{r['buy_ef']:.1f} months",GREEN_OK if r["buy_ef"]>=3 else RED_WARN),
        ]

        for label,val,color in metrics:
            cell=tk.Frame(strip,bg=CARD_BG); cell.pack(side="left",expand=True,fill="both",padx=1)
            tk.Label(cell,text=label,font=self.small_font,bg=CARD_BG,
                     fg=GRAY_LIGHT).pack(pady=(8,0))
            tk.Label(cell,text=val,font=tkfont.Font(family="Menlo",size=14,weight="bold"),
                     bg=CARD_BG,fg=color).pack(pady=(2,8))

    # ── Detail text ─────────────────────────
    def _display_detail(self,r,p):
        t=self.result_text; t.config(state="normal"); t.delete("1.0","end")
        def line(text="",tag=None): t.insert("end",text+"\n",tag)
        def kv(l,v,tag=None): t.insert("end",f"  {l:<34}{v}\n",tag or "kv")

        sep="-"*62
        w=r["advantage"]; c="green" if w=="BUY" else "orange"
        loc=p.get("location",""); ls=f" in {loc}" if loc else ""

        line()
        line(f"  VERDICT: {w} wins by {fmt_usd(r['advantage_amount'])}",c)
        line(f"     over {r['hold_years']} years{ls}","sub")
        line()
        if w=="BUY":
            line("  Buying and selling after "+
                 f"{r['hold_years']} years leaves you {fmt_usd(r['advantage_amount'])}","explain")
            line("  richer than renting and investing the difference.","explain")
        else:
            line("  Renting and investing your would-be down payment leaves","explain")
            line(f"  you {fmt_usd(r['advantage_amount'])} richer after {r['hold_years']} years.","explain")
        line(); line(sep,"sub"); line()

        line("  AFFORDABILITY CHECK","header"); line()
        kv("Monthly Take-Home",fmt_usd(r["monthly_net"]))
        kv("Buy: Housing/Take-Home",f"{r['buy_housing_pct']:.0f}%")
        kv("Rent: Housing/Take-Home",f"{r['rent_housing_pct']:.0f}%")
        line()
        gm=p["annual_salary"]/12
        bhg=(r["avg_buy_mo"]/gm*100) if gm>0 else 0
        kv("Buy: Housing/Gross (28% rule)",
           f"{bhg:.0f}%  {'PASS' if bhg<=28 else 'OVER LIMIT'}",
           "ok" if bhg<=28 else "warn")
        kv("Buy: DTI (36% rule)",
           f"{r['buy_dti']:.0f}%  {'PASS' if r['buy_dti']<=36 else 'OVER LIMIT'}",
           "ok" if r["buy_dti"]<=36 else "warn")
        kv("Rent: DTI (36% rule)",
           f"{r['rent_dti']:.0f}%  {'PASS' if r['rent_dti']<=36 else 'OVER LIMIT'}",
           "ok" if r["rent_dti"]<=36 else "warn")
        line()
        kv("Buy: Left Over",f"{fmt_usd(r['buy_left'])}/mo","green" if r["buy_left"]>0 else "red")
        kv("Rent: Left Over",f"{fmt_usd(r['rent_left'])}/mo","green" if r["rent_left"]>0 else "red")
        kv("Emergency Fund",f"{r['buy_ef']:.1f} mo of buy costs",
           "green" if r["buy_ef"]>=3 else "red")

        line(); line(sep,"sub"); line()
        line("  BUY SCENARIO","header"); line()
        kv("Down Payment",fmt_usd(r["down_payment"]))
        kv("Loan Amount",fmt_usd(r["loan_amount"]))
        kv("Monthly Payment",fmt_usd(r["monthly_pmt"]))
        kv("Total Interest",fmt_usd(r["total_interest"]),"red")
        kv("Total Prop Tax",fmt_usd(r["total_prop_tax"]))
        kv("Total Insurance",fmt_usd(r["total_insurance"]))
        kv("Total Maintenance",fmt_usd(r["total_maint"]))
        kv("Total Outflows",fmt_usd(r["total_buy_outflows"]),"red")
        line()
        kv("Future Home Value",fmt_usd(r["future_home_value"]),"green")
        kv("Future $/Sq Ft",fmt_usd2(r["future_price_sqft"]))
        kv("Remaining Mortgage",fmt_usd(r["remaining_balance"]))
        kv("Selling Costs",fmt_usd(r["closing_sell_cost"]))
        kv("Net Sale Proceeds",fmt_usd(r["net_sale_proceeds"]),"green")
        line()
        line(f"  Sell after {r['hold_years']} years => {fmt_usd(r['net_sale_proceeds'])} cash in hand.","explain")
        line()
        kv("NPV",fmt_usd(r["buy_npv"]),"green" if r["buy_npv"]>0 else "red")
        kv("IRR",fmt_pct(r["buy_irr"]),"green" if r["buy_irr"] and r["buy_irr"]>0 else "red")
        kv("Buyer Wealth",fmt_usd(r["buyer_net_wealth"]),"bold")

        line(); line(sep,"sub"); line()
        line("  RENT SCENARIO","header"); line()
        kv("Starting Rent",fmt_usd(p["monthly_rent"]))
        kv("Total Rent Paid",fmt_usd(r["total_rent_paid"]),"red")
        cap=r["down_payment"]+p["home_price"]*p["closing_buy"]/100
        kv("Capital Invested",fmt_usd(cap))
        kv(f"Portfolio @ {p['invest_return']:.1f}%",fmt_usd(r["renter_terminal"]),"green")
        line()
        line(f"  Invest {fmt_usd(cap)} instead of buying.","explain")
        line(f"  After {r['hold_years']} years it grows to {fmt_usd(r['renter_terminal'])}.","explain")
        line()
        kv("NPV",fmt_usd(r["rent_npv_with_invest"]),"green" if r["rent_npv_with_invest"]>0 else "red")
        kv("IRR",fmt_pct(r["rent_irr"]),"green" if r["rent_irr"] and r["rent_irr"]>0 else "red")
        kv("Renter Wealth",fmt_usd(r["renter_net_wealth"]),"bold")

        line(); line(sep,"sub"); line()
        line("  OPPORTUNITY COST","header"); line()
        opp=r["renter_terminal"]-r["buyer_net_wealth"]
        if opp>0:
            kv("Cost of Buying",fmt_usd(abs(opp)),"red")
            line(f"  Buying costs you {fmt_usd(abs(opp))} in missed investment growth.","explain")
        else:
            kv("Benefit of Buying",fmt_usd(abs(opp)),"green")
            line(f"  Buying puts you {fmt_usd(abs(opp))} ahead of investing.","explain")

        line(); line(sep,"sub"); line()
        line("  GLOSSARY","header"); line()
        line("  NPV: Future money converted to today's dollars. Positive = good.","explain")
        line(f"  IRR: Your effective annual return. Compare to {p['discount_rate']:.1f}% hurdle.","explain")
        line("  Opportunity Cost: What you give up by choosing one path.","explain")
        line("  28/36 Rule: Housing < 28% gross; total debt < 36% gross.","explain")
        line("  DTI: Debt-to-income ratio (housing + debts / gross income).","explain")
        line()
        t.config(state="disabled"); t.see("1.0")


if __name__=="__main__":
    App().mainloop()