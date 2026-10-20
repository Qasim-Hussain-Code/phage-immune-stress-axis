"""Publication-style audit and immune figures from actual retrieved records."""
import json
import os
from .io import read_csv,write_csv
from .reporting import NAMES,CONTRAST_NAMES


def generate(root,config):
    os.environ['MPLCONFIGDIR']=str(root/'.cache/matplotlib')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,
                         'axes.spines.right':False,'pdf.fonttype':42,'savefig.dpi':300})
    out=root/'figures'
    def save(fig,name):
        fig.savefig(out/(name+'.png'),dpi=300,bbox_inches='tight',facecolor='white')
        fig.savefig(out/(name+'.pdf'),bbox_inches='tight',facecolor='white',
                    metadata={'Title':name,'Author':'Qasim Hussain','CreationDate':None})
        plt.close(fig)
    inventory=read_csv(root/'results/tables/sequencing_inventory.csv')
    source=read_csv(root/'results/tables/source_inventory.csv')
    availability=json.loads((root/'results/reports/sample_audit_summary.json').read_text())
    source_counts={r['experiment_id']:int(r['nonempty_animal_rows']) for r in source}
    group_counts={r['experiment_id']:json.loads(r['group_counts_json']) for r in source}
    categories=availability['sequencing_category_counts']
    data=[{'category':r['sample_type'],'count':r['sample_count'],'unit':'sequencing specimen','source':r['accession']}
          for r in inventory if r['accession']=='PRJNA970614']
    data.extend({'category':r['experiment_id'],'count':r['nonempty_animal_rows'],'unit':'source workbook animal row','source':r['source_sheet']} for r in source)
    data.append({'category':'initial_enriched_pools_across_group_time','count':12,'unit':'published pool profiles, membership unresolved','source':'article Fig1 caption: 3 per group/time'})
    write_csv(root/'results/tables/figure1_data.csv',data)
    fig,ax=plt.subplots(figsize=(10,5.2));ax.axis('off')
    boxes=[(.02,.55,.43,.36,f'Initial stress experiment\nControl {group_counts["study_i"]["ctr"]}; Stress {group_counts["study_i"]["ctr_stress"]} phenotype rows\n3 pools/group before and after stress\nPool membership across time unresolved'),
           (.54,.55,.43,.36,f'FVT experiment\nControl {group_counts["study_ii"]["ctr"]}; Stress {group_counts["study_ii"]["ctr_stress"]}; FVT Stress {group_counts["study_ii"]["fvt_stress"]}\nRecipient bulk profiles before/after\n{availability["principal_specimen_count"]} specimens: {categories["individual_recipient_bulk_metagenome"]} bulk; {categories["pooled_fecal_virome"]} pools; {categories["transplant_inoculum"]} inocula'),
           (.02,.09,.43,.31,'Individual immune measurements\nLinked to behavior within source rows\nAssay-specific missingness retained\nNo baseline of chronic immune change'),
           (.54,.09,.43,.31,f'Community analysis gate\nIndividual bulk viral profiles published\nMatrices and mouse crosswalk unavailable\n{availability["verified_virome_immune_matches"]} usable virome-immune matches')]
    for x,y,w,h,label in boxes:
        ax.add_patch(plt.Rectangle((x,y),w,h,facecolor='#eef4f7',edgecolor='#35586b',lw=1))
        ax.text(x+.02,y+h-.04,label,va='top',fontsize=10,linespacing=1.5)
    ax.annotate('',xy=(.235,.41),xytext=(.235,.54),arrowprops={'arrowstyle':'->','color':'#35586b'})
    ax.annotate('',xy=(.755,.41),xytext=(.755,.54),arrowprops={'arrowstyle':'->','color':'#35586b'})
    ax.set_title('Study structure and public-data availability',loc='left',fontweight='bold',pad=14)
    save(fig,'figure1_design')

    raw=read_csv(root/'data/processed/immune_long.csv')
    endpoints=config['immune']['endpoints']
    selected=[r for r in raw if r['experiment_id']=='study_ii' and r['endpoint'] in endpoints]
    write_csv(root/'results/tables/figure4_data.csv',selected)
    contrasts=read_csv(root/'results/tables/immune_contrasts.csv')
    groups=['ctr','ctr_stress','fvt_stress'];labels=['Control','Control\nStress','FVT\nStress']
    colors=['#46799b','#bb6246','#55856b']
    fig,axes=plt.subplots(2,3,figsize=(12,7),gridspec_kw={'height_ratios':[1.4,1]})
    for column,endpoint in enumerate(endpoints):
        ax=axes[0,column]
        for i,group in enumerate(groups):
            values=[float(r['value']) for r in selected if r['endpoint']==endpoint and r['group']==group and r['observation_status']=='observed']
            # Deterministic symmetric offsets are for legibility only.
            offsets=[(j-(len(values)-1)/2)*.035 for j in range(len(values))]
            ax.scatter([i+x for x in offsets],values,color=colors[i],s=30,alpha=.85,zorder=3)
            ax.plot([i-.19,i+.19],[sum(values)/len(values)]*2,color='black',lw=1.8)
        ns=[sum(r['endpoint']==endpoint and r['group']==g and r['observation_status']=='observed' for r in selected) for g in groups]
        ax.set_xticks(range(3),[f'{label}\n(n={n})' for label,n in zip(['Control','Stress','FVT Stress'],ns)])
        ax.set_ylabel('Percent of parent population' if column<2 else 'TNF-alpha (pg/mL)')
        title={'ly6chi_monocytes':'Basal LY6Chi monocytes','ly6chi_monocytes_cd62':'Basal CD62L-positive monocytes','tnfa_splenocyte_unstimulated':'Unstimulated splenocyte TNF-alpha'}[endpoint]
        ax.set_title(title,fontsize=10,fontweight='bold')
        ax=axes[1,column]
        rows=[r for r in contrasts if r['endpoint']==endpoint]
        for y,row in enumerate(rows):
            v=float(row['mean_difference']);lo=float(row['ci_low']);hi=float(row['ci_high'])
            ax.errorbar(v,y,xerr=[[v-lo],[hi-v]],fmt='o',color='#35586b',capsize=3)
            ax.text(.99,y+.18,f"q={float(row['q_value']):.3g}",transform=ax.get_yaxis_transform(),ha='right',fontsize=8)
        ax.axvline(0,color='.7',lw=1,ls='--');ax.set_ylim(-.6,1.6)
        ax.set_yticks([0,1],['Stress - Control','FVT Stress - Stress'] if column==0 else ['',''])
        ax.set_xlabel('Difference (percentage points)' if column<2 else 'Difference (pg/mL)')
    fig.suptitle('Separate exploratory immune outcomes',x=.03,ha='left',fontweight='bold',fontsize=14)
    fig.text(.03,.01,'Dots: observed animals; bars: means. Stress: control treatment with stress. Welch intervals: pointwise 95%; BH family: six tests.',fontsize=9)
    fig.tight_layout(rect=[0,.045,1,.95],h_pad=3)
    save(fig,'figure4_immune')

    eligibility=read_csv(root/'results/tables/hypothesis_eligibility.csv')
    observed_counts=[int(r['n_observed']) for r in read_csv(root/'results/tables/immune_summary.csv')]
    min_n,max_n=min(observed_counts),max(observed_counts)
    limitation=[{'measurement':'processed_virome_profiles_retrieved','count':availability['processed_virome_profiles_retrieved'],'status':'unavailable'},
                {'measurement':'verified_virome_immune_matches','count':availability['verified_virome_immune_matches'],'status':'unavailable'},
                {'measurement':'selected_endpoint_min_n_per_group','count':min_n,'status':'observed'},
                {'measurement':'selected_endpoint_max_n_per_group','count':max_n,'status':'observed'}]
    write_csv(root/'results/tables/figure5_data.csv',limitation)
    fig,ax=plt.subplots(figsize=(12,4.5));ax.axis('off')
    rows=[('Viral community matrix','Unavailable in inspected processed release'),
          ('Verified mouse crosswalk','Unavailable; literal IDs cannot be repaired by guessing'),
          ('Individual immune outcomes',f'Available; endpoints have {min_n}-{max_n} observations/group'),
          ('Matched viral and immune profiles',f'{availability["verified_virome_immune_matches"]} processed profiles matched to immune outcomes'),
          ('Scientific consequence','Phageome stability versus immune response remains unanswered')]
    for i,(left,right) in enumerate(rows):
        y=.88-i*.18
        ax.text(.015,y,left,fontweight='bold',va='center',fontsize=9)
        ax.text(.38,y,right,va='center',fontsize=9)
        ax.axhline(y-.075,color='.88',lw=.8)
    ax.set_title('Why no phage-immune association was fitted',loc='left',fontweight='bold',pad=15)
    save(fig,'figure5_linkage_limit')

    sensitivity=read_csv(root/'results/tables/immune_sensitivity.csv')
    joined=[]
    for r in sensitivity:
        match=next(x for x in contrasts if (x['endpoint'],x['contrast'])==(r['endpoint'],r['contrast']))
        joined.append({**r,'full_mean_difference':match['mean_difference'],'welch_p_value':match['p_value'],'welch_q_value':match['q_value']})
    write_csv(root/'results/tables/figure7_data.csv',joined)
    fig,axes=plt.subplots(1,3,figsize=(12,3.8))
    for column,(ax,endpoint) in enumerate(zip(axes,endpoints)):
        for y,row in enumerate(r for r in joined if r['endpoint']==endpoint):
            lo=float(row['loo_mean_difference_min']);hi=float(row['loo_mean_difference_max']);v=float(row['full_mean_difference'])
            ax.hlines(y,lo,hi,color='#46799b',lw=5,alpha=.65)
            ax.plot(v,y,'o',color='black')
        ax.axvline(0,color='.7',ls='--',lw=1);ax.set_ylim(-.6,1.6)
        ax.set_yticks([0,1],['Stress - Control','FVT Stress - Stress'] if column==0 else ['',''])
        ax.set_xlabel('Difference (percentage points)' if column<2 else 'Difference (pg/mL)');ax.set_title(NAMES[endpoint].replace(' fraction of LY6Chi monocytes',' monocytes').replace(' proportion',''),fontsize=9)
    fig.suptitle('Influence of omitting one observed animal',x=.02,ha='left',fontweight='bold',fontsize=13)
    fig.text(.02,.01,'Black: full estimate. Blue: leave-one-animal-out range, not a confidence interval. Rank sensitivity is in the source table.',fontsize=9)
    fig.tight_layout(rect=[0,.06,1,.9])
    save(fig,'figure7_robustness')

    original=read_csv(root/'results/tables/original_method_replication.csv')
    comparison=[]
    for row in contrasts:
        comparison.append({'endpoint':row['endpoint'],'contrast':row['contrast'],'method':'Welch',
            'mean_difference':row['mean_difference'],'ci_low':row['ci_low'],'ci_high':row['ci_high'],
            'p_value':row['p_value'],'interval_scope':'pointwise 95%','effect_units':row['effect_units']})
        match=next(r for r in original if r['record_type']=='tukey_kramer' and
                   (r['endpoint'],r['contrast'])==(row['endpoint'],row['contrast']))
        comparison.append({'endpoint':row['endpoint'],'contrast':row['contrast'],'method':'Original Tukey-Kramer',
            'mean_difference':match['effect'],'ci_low':match['ci_low'],'ci_high':match['ci_high'],
            'p_value':match['p_value'],'interval_scope':'simultaneous 95% across 3 pairs within endpoint',
            'effect_units':match['effect_units']})
    write_csv(root/'results/tables/figure8_data.csv',comparison)
    fig,axes=plt.subplots(1,3,figsize=(12,4.7))
    for column,(ax,endpoint) in enumerate(zip(axes,endpoints)):
        for y,label in enumerate(['ctr_stress_minus_ctr','fvt_stress_minus_ctr_stress']):
            for method,offset,color in [('Welch',-.13,'#46799b'),('Original Tukey-Kramer',.13,'#b87643')]:
                row=next(r for r in comparison if (r['endpoint'],r['contrast'],r['method'])==(endpoint,label,method))
                effect=float(row['mean_difference']);low=float(row['ci_low']);high=float(row['ci_high'])
                ax.errorbar(effect,y+offset,xerr=[[effect-low],[high-effect]],fmt='o',color=color,capsize=3,ms=4)
        ax.axvline(0,color='.7',ls='--',lw=1);ax.set_ylim(-.55,1.55)
        ax.set_yticks([0,1],['Stress - Control','FVT Stress - Stress'] if column==0 else ['',''])
        ax.set_xlabel('Difference (percentage points)' if column<2 else 'Difference (pg/mL)')
        ax.set_title({'ly6chi_monocytes':'Basal LY6Chi monocytes',
                      'ly6chi_monocytes_cd62':'Basal CD62L-positive monocytes',
                      'tnfa_splenocyte_unstimulated':'Unstimulated splenocyte TNF-alpha'}[endpoint],fontsize=9)
    from matplotlib.lines import Line2D
    fig.legend([Line2D([0],[0],color='#46799b',marker='o'),Line2D([0],[0],color='#b87643',marker='o')],
               ['Welch: unequal variances, pointwise 95%','Original Tukey-Kramer: pooled variance, simultaneous 95%'],
               loc='lower center',bbox_to_anchor=(.5,.07),ncol=2,frameon=False,fontsize=9)
    fig.suptitle('Variance and multiplicity assumptions change immune intervals',x=.02,ha='left',fontweight='bold',fontsize=13)
    fig.text(.02,.015,'Identical observed values and mean differences. Tukey coverage concerns all 3 pairs within each endpoint; the original across-outcome BH family is not reconstructed.',fontsize=8)
    fig.tight_layout(rect=[0,.2,1,.9])
    save(fig,'figure8_method_comparison')
    return {'figures':5,'png_outputs':5,'vector_pdf_outputs':5,'unsupported_figures':[2,3,6]}
