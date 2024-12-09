USE GRACE
set transaction  isolation level read uncommitted

--***********************************************************
--* Variablen
--***********************************************************

declare @sgf		as nvarchar(4)
declare @DUMMY		as nvarchar(10)
set @sgf = '4'
set @DUMMY = 'OHNE'

--***********************************************************
--* LOGIK
--***********************************************************

SELECT	
		MV_Vorgang.mv_vorgang, MV_Vorgang.mv_kunde, KD_Stamm.kd_name1,  MV_Vorgang.mv_ve, MV_Vorgang.mv_kundenprojekt, 
		Baustelle = case when MV_Anschriften.mva_name1 is null or MV_Anschriften.mva_name1 = '' then MV_Kundenprojekte.mvkp_bezeichnung else '' end,
		MV_Anschriften.mva_plz, MV_Anschriften.mva_ort,  
		MV_Kundenprojekte.mvkp_co_projekt
		,mv_trans_stat
		,AKUN.[mva_ktk_mail]
		,AKUN.[mva_ktk_mail2]
		
FROM	MV_Vorgang 
		INNER JOIN MV_Anschriften				ON MV_Vorgang.mv_vorgang = MV_Anschriften.mva_vorgang AND MV_Anschriften.mva_art = N'BAU'
		INNER JOIN MV_Anschriften	AKUN		ON MV_Vorgang.mv_vorgang = AKUN.mva_vorgang AND  AKUN.mva_art = N'KUN'
		INNER JOIN OR_Vertriebseinheiten		ON OR_Vertriebseinheiten.orv_ve = MV_Vorgang.mv_ve
		INNER JOIN OR_Vertriebsorte				ON OR_Vertriebseinheiten.orv_vo = OR_Vertriebsorte.orvs_ort 
		INNER JOIN OR_Vertriebsbereiche			ON OR_Vertriebsorte.orvs_vb = OR_Vertriebsbereiche.orvb_id
		INNER JOIN SY_Transaktionsarten			ON SY_Transaktionsarten.syta_id = MV_Vorgang.mv_trans_art
		INNER JOIN SY_Transaktionstypen			ON SY_Transaktionsarten.syta_typ = SY_Transaktionstypen.sytt_typ
		INNER JOIN KD_Stamm						ON mv_kunde = kd_kunde
		LEFT OUTER JOIN MV_Kundenprojekte		ON MV_Vorgang.mv_kundenprojekt = MV_Kundenprojekte.mvkp_projekt

--		LEFT OUTER JOIN OR_Mitarbeiter			ON SV_Ressourcen.svr_mitarbeiter = OR_Mitarbeiter.orm_persnr

WHERE	OR_Vertriebsbereiche.orvb_er_region = @sgf				-- nur EKW Vorgaenge
		AND (SY_Transaktionstypen.sytt_kategorie = N'AUFTRAG')	-- nur Aufträge
		AND mv_ende is null										-- keine abgeschlossenen 
		AND mv_trans_stat <> 'STO'								-- keine Stornos