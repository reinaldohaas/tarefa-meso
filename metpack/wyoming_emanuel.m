function [P, PL, TRDBAR, TPDBAR, CAPE] = wyoming_emanuel(arq_sounding, corte)
% WYOMING_EMANUEL  Tradução para MATLAB do programa wyoming.f de Kerry Emanuel
% (https://texmex.mit.edu/pub/emanuel/soundings/wyoming.f). Dispensa compilador Fortran.
%
% Lê o sounding.txt no formato do wyoming.f (10 linhas de cabeçalho; depois linhas
% FORMAT(1X,F6.1,9X,F5.1,2X,F5.1) com p, T e Td) e calcula, para parcelas originadas nos
% 20 níveis mais baixos (a cada 5 hPa), a diferença de temperatura de densidade
% parcela - ambiente nas ascensões reversível e pseudoadiabática, a CAPE e a DCAPE.
%
% Uso:
%   [p, porig, tdifrev, tdifpseudo, cape] = wyoming_emanuel('sounding.txt');
%   corte = true reproduz o piso de -4 K do wyoming.f original (padrão: false).
%
% Saídas (mesmas do wyoming.f):
%   P       - níveis para os quais a parcela é elevada (p.out)
%   PL      - níveis de origem (porig.out)
%   TRDBAR  - matriz reversível, linhas = P, colunas = PL (tdifrev.out)
%   TPDBAR  - matriz pseudoadiabática (tdifpseudo.out)
%   CAPE    - colunas de cape.out: origem, PA rev, PA pse, NA rev, NA pse, CAPE rev, CAPE pse, DCAPE

if nargin < 1 || isempty(arq_sounding), arq_sounding = 'sounding.txt'; end
if nargin < 2, corte = false; end

NK = 20;
CPD = 1005.7; CL = 2500.0; CPVMCL = 2320.0; RV = 461.5; RD = 287.04;
EPS = RD / RV; ALV0 = 2.501E6;

% --- leitura (mesmos filtros do wyoming.f) ---
linhas = regexp(fileread(arq_sounding), '\r?\n', 'split');
PTEM = []; TTEM = []; RTEM = [];
for k = 11:numel(linhas)
    l = linhas{k};
    if ~isempty(strfind(l, '</PRE>')) || isempty(strtrim(l)), break; end
    l = [l repmat(' ', 1, 30)];
    pk = str2double(l(2:7)); tk = str2double(l(17:21)); rk = str2double(l(24:28));
    if any(isnan([pk tk rk])), break; end
    if pk < 78.0 || tk > 100.0 || rk > 100.0, continue; end
    PTEM(end+1) = pk; TTEM(end+1) = max(tk, -200.0); RTEM(end+1) = rk; %#ok<AGROW>
end
EVTEM = 6.112 * exp(17.67 * RTEM ./ (243.5 + RTEM));
ESTEM = 6.112 * exp(17.67 * TTEM ./ (243.5 + TTEM));
EVTEM = min(EVTEM, ESTEM);
RTEM = 0.622 * EVTEM ./ (PTEM - EVTEM);
TTEM = TTEM + 273.15;
N = numel(PTEM);

% --- interpolação a cada 5 hPa ---
NL = fix((1005.0 - PTEM(N)) / 5.0 + 0.001);
P = zeros(NL, 1); T = P; R = P; EV = P; ES = P;
P(1) = PTEM(1); T(1) = TTEM(1); R(1) = RTEM(1); EV(1) = EVTEM(1); ES(1) = ESTEM(1);
for i = 2:NL
    P(i) = 1005.0 - 5.0 * i;
    for j = 2:N
        if PTEM(j) <= P(i)
            w1 = (PTEM(j-1) - P(i)); w2 = (P(i) - PTEM(j)); d = PTEM(j-1) - PTEM(j);
            T(i)  = (TTEM(j)  * w1 + TTEM(j-1)  * w2) / d;
            R(i)  = (RTEM(j)  * w1 + RTEM(j-1)  * w2) / d;
            EV(i) = (EVTEM(j) * w1 + EVTEM(j-1) * w2) / d;
            ES(i) = (ESTEM(j) * w1 + ESTEM(j-1) * w2) / d;
            break
        end
    end
end
N = NL;
TVE = T .* (1 + R / EPS) ./ (1 + R);          % temperatura virtual do ambiente

TVRDIF = zeros(NK, N); TVPDIF = zeros(NK, N); TVD = zeros(NK, 1); PL = zeros(NK, 1);
for I = 1:NK
    PL(I) = P(I);
    RS = EPS * ES(I) / (P(I) - ES(I));
    ALV = ALV0 - CPVMCL * (T(I) - 273.15);
    EM = max(EV(I), 1.0E-6);
    S  = (CPD + R(I) * CL) * log(T(I)) - RD * log(P(I) - EV(I)) + ALV * R(I) / T(I) - R(I) * RV * log(EM / ES(I));
    SP = CPD * log(T(I)) - RD * log(P(I) - EV(I)) + ALV * R(I) / T(I) - R(I) * RV * log(EM / ES(I));
    AH = (CPD + R(I) * CL) * T(I) + ALV * R(I);
    % parcela saturada por processo de bulbo úmido (topo da corrente descendente)
    SLOPE = CPD + ALV * ALV * RS / (RV * T(I) * T(I));
    TG = T(I); RG = RS;
    for k = 1:20
        ALV1 = ALV0 - CPVMCL * (TG - 273.15);
        AHG = (CPD + CL * RG) * TG + ALV1 * RG;
        TG = TG + (AH - AHG) / SLOPE;
        TC = TG - 273.15; ENEW = 6.112 * exp(17.67 * TC / (243.5 + TC));
        RG = EPS * ENEW / (P(I) - ENEW);
    end
    EG = RG * P(I) / (EPS + RG);
    SPD = CPD * log(TG) - RD * log(P(I) - EG) + ALV1 * RG / TG;
    TVD(I) = TG * (1 + RG / EPS) / (1 + RG) - TVE(I);
    if P(I) < 100.0, TVD(I) = 0.0; end
    RGD0 = RG; TGD0 = TG;
    % nível de condensação por levantamento
    RH = min(R(I) / RS, 1.0);
    CHI = T(I) / (1669.0 - 122.0 * RH - T(I));
    PLCL = 1.0;
    if RH > 0.0, PLCL = P(I) * RH^CHI; end
    % ascensão
    SUM = 0.0; RG0 = R(I); TG0 = T(I);
    for J = I:N
        RS = EPS * ES(J) / (P(J) - ES(J));
        ALV = ALV0 - CPVMCL * (T(J) - 273.15);
        SL  = (CPD + R(I) * CL + ALV * ALV * RS / (RV * T(J) * T(J))) / T(J);
        SLP = (CPD + RS * CL + ALV * ALV * RS / (RV * T(J) * T(J))) / T(J);
        if P(J) >= PLCL
            TLR = T(I) * (P(J) / P(I))^(RD / CPD);
            TVRDIF(I, J) = TLR * (1 + R(I) / EPS) / (1 + R(I)) - TVE(J);
            TVPDIF(I, J) = TVRDIF(I, J);
        else
            TG = T(J); RG = RS;                       % reversível
            for k = 1:20
                EM = RG * P(J) / (EPS + RG);
                ALV = ALV0 - CPVMCL * (TG - 273.15);
                SG = (CPD + R(I) * CL) * log(TG) - RD * log(P(J) - EM) + ALV * RG / TG;
                TG = TG + (S - SG) / SL;
                TC = TG - 273.15; ENEW = 6.112 * exp(17.67 * TC / (243.5 + TC));
                RG = EPS * ENEW / (P(J) - ENEW);
            end
            TVRDIF(I, J) = TG * (1 + RG / EPS) / (1 + R(I)) - TVE(J);
            TG = T(J); RG = RS;                       % pseudoadiabática
            for k = 1:20
                CPW = 0.0;
                if J > 1
                    CPW = SUM + CL * 0.5 * (RG0 + RG) * (log(TG) - log(TG0));
                end
                EM = RG * P(J) / (EPS + RG);
                ALV = ALV0 - CPVMCL * (TG - 273.15);
                SPG = CPD * log(TG) - RD * log(P(J) - EM) + CPW + ALV * RG / TG;
                TG = TG + (SP - SPG) / SLP;
                TC = TG - 273.15; ENEW = 6.112 * exp(17.67 * TC / (243.5 + TC));
                RG = EPS * ENEW / (P(J) - ENEW);
            end
            TVPDIF(I, J) = TG * (1 + RG / EPS) / (1 + RG) - TVE(J);
            RG0 = RG; TG0 = TG; SUM = CPW;
        end
    end
    % corrente descendente (só para a DCAPE)
    if I > 1
        SUM2 = 0.0;
        for J = I-1:-1:1
            RS = EPS * ES(J) / (P(J) - ES(J));
            ALV = ALV0 - CPVMCL * (T(J) - 273.15);
            SLP = (CPD + RS * CL + ALV * ALV * RS / (RV * T(J) * T(J))) / T(J);
            TG = T(J); RG = RS;
            for k = 1:20
                CPW = SUM2 + CL * 0.5 * (RGD0 + RG) * (log(TG) - log(TGD0));
                EM = RG * P(J) / (EPS + RG);
                ALV = ALV0 - CPVMCL * (TG - 273.15);
                SPG = CPD * log(TG) - RD * log(P(J) - EM) + CPW + ALV * RG / TG;
                TG = TG + (SPD - SPG) / SLP;
                TC = TG - 273.15; ENEW = 6.112 * exp(17.67 * TC / (243.5 + TC));
                RG = EPS * ENEW / (P(J) - ENEW);
            end
            SUM2 = CPW; TGD0 = TG; RGD0 = RG;
            TVPDIF(I, J) = TG * (1 + RG / EPS) / (1 + RG) - TVE(J);
            if P(I) < 100.0, TVPDIF(I, J) = 0.0; end
            TVPDIF(I, J) = min(TVPDIF(I, J), 0.0);
            TVRDIF(I, J) = 0.0;
        end
    end
end

% --- áreas positiva e negativa, CAPE e DCAPE ---
CAPE = zeros(NK, 8);
for I = 1:NK
    INBR = 1; INBP = 1;
    for J = N:-1:I
        if TVRDIF(I, J) > 0.0, INBR = max(INBR, J); end
        if TVPDIF(I, J) > 0.0, INBP = max(INBP, J); end
    end
    PAR = 0; NAR = 0; PAP = 0; NAP = 0; CR = 0; CP = 0; DC = 0;
    if INBR > I
        for J = I+1:INBR
            TVM = 0.5 * (TVRDIF(I, J) + TVRDIF(I, J-1)); PM = 0.5 * (P(J) + P(J-1));
            if TVM <= 0, NAR = NAR - RD * TVM * (P(J-1) - P(J)) / PM;
            else,        PAR = PAR + RD * TVM * (P(J-1) - P(J)) / PM; end
        end
        CR = PAR - NAR;
    end
    if INBP > I
        for J = I+1:INBP
            TVM = 0.5 * (TVPDIF(I, J) + TVPDIF(I, J-1)); PM = 0.5 * (P(J) + P(J-1));
            if TVM <= 0, NAP = NAP - RD * TVM * (P(J-1) - P(J)) / PM;
            else,        PAP = PAP + RD * TVM * (P(J-1) - P(J)) / PM; end
        end
        CP = PAP - NAP;
    end
    if I > 1
        for J = I-1:-1:1
            TVDIFM = TVPDIF(I, J+1);
            if I == J + 1, TVDIFM = TVD(I); end
            TVM = 0.5 * (TVPDIF(I, J) + TVDIFM); PM = 0.5 * (P(J) + P(J+1));
            if TVM < 0, DC = DC - RD * TVM * (P(J) - P(J+1)) / PM; end
        end
    end
    CAPE(I, :) = [PL(I) PAR PAP NAR NAP CR CP DC];
end

% --- matrizes no formato de tdifrev.out / tdifpseudo.out (linhas = P, colunas = origem) ---
TRDBAR = zeros(N, NK); TPDBAR = zeros(N, NK);
for I = 1:NK
    for J = I:N
        TRDBAR(J, I) = TVRDIF(I, J);
        TPDBAR(J, I) = TVPDIF(I, J);
    end
end
if corte
    TRDBAR(TRDBAR ~= 0) = max(TRDBAR(TRDBAR ~= 0), -4.0);
    TPDBAR(TPDBAR ~= 0) = max(TPDBAR(TPDBAR ~= 0), -4.0);
end
end
