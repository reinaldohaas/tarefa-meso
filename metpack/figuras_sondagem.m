function F = figuras_sondagem(data, rotulo, pasta, p_topo)
% FIGURAS_SONDAGEM  Figuras de uma sondagem com as rotinas do metpack:
%   1) Skew-T de Emanuel (skewt.m) com barbelas de vento (windbarb.m) e hodógrafo
%      com o movimento de tempestade de Bunkers (left-mover e right-mover);
%   2) perfis de theta, theta_e e theta_es (thermo_td.m), N^2 e S até P_TOPO.
%
% Uso:
%   [data, header] = getsounding_wyoming(83971, 1995, 12, 24, 12);
%   F = figuras_sondagem(data, 'INSTÁVEL 24/12/1995 12Z', 'emanuel_19951224_12');
%
% data: colunas de getsounding_wyoming (P hPa, z m, T C, Td C, UR %, r g/kg, DIR graus, VEL nós, ...)
% F.bunkers_lm, F.bunkers_rm: vetores [u v] em m/s; F.theta, F.thetae, F.thetaes, F.N2, F.S, F.p.

if nargin < 3 || isempty(pasta), pasta = '.'; end
if nargin < 4 || isempty(p_topo), p_topo = 200; end

ok = all(isfinite(data(:, 1:4)), 2) & data(:, 1) >= 100;    % o skewt.m vai de 1050 a 100 hPa
d = data(ok, :);
[~, io] = sort(d(:, 1), 'descend'); d = d(io, :);
p = d(:, 1); z = d(:, 2); T = d(:, 3); Td = d(:, 4); UR = d(:, 5) / 100;
temvento = isfinite(d(:, 7)) & isfinite(d(:, 8));

% ---------------- vento e Bunkers ----------------
[u_kt, v_kt] = wswd_to_uv(d(:, 8), d(:, 7));          % nós
u = u_kt * 0.514444; v = v_kt * 0.514444;             % m/s
h = z - z(1);                                         % altura acima da superfície
F.bunkers_lm = [NaN NaN]; F.bunkers_rm = [NaN NaN];
if nnz(temvento) >= 4
    pw = p(temvento); hw = h(temvento); uw = u(temvento); vw = v(temvento);
    vm = media_camada(pw, hw, uw, vw, 0, 6000);         % vento médio 0-6 km (ponderado pela pressão)
    v05 = media_camada(pw, hw, uw, vw, 0, 500);
    v55 = media_camada(pw, hw, uw, vw, 5500, 6000);
    cis = v55 - v05;
    desvio = [cis(2), -cis(1)] * 7.5 / norm(cis);       % 7,5 m/s perpendicular ao cisalhamento
    F.bunkers_rm = vm + desvio;
    F.bunkers_lm = vm - desvio;                          % ciclônico no Hemisfério Sul
end

fig1 = figure('Name', ['Skew-T e hodógrafo - ' rotulo], 'Color', 'w', 'Position', [40 40 1350 650]);
% Skew-T de Emanuel
ax1 = axes('Position', [0.06 0.11 0.50 0.80]);
skewt(p, T, min(max(UR, 0), 1));
axis(ax1, [-40 50 100 1050]);
title(ax1, rotulo);
% barbelas (windbarb.m) num eixo transparente sobre o Skew-T, em coordenadas normalizadas
% (o windbarb.m desenha em eixos lineares; aqui a altura acompanha log(p) do Skew-T)
ax2 = axes('Position', get(ax1, 'Position'), 'Color', 'none', 'Visible', 'off', ...
           'XLim', [0 1], 'YLim', [0 1]);
hold(ax2, 'on');
ynorm = @(pp) (log(1050) - log(pp)) / (log(1050) - log(100));
pb = 1050;
for k = 1:numel(p)
    if temvento(k) && p(k) <= pb
        windbarb(0.93, ynorm(p(k)), d(k, 8), d(k, 7), 0.035, 1, 'k');
        pb = p(k) - 25;                                  % uma barbela a cada ~25 hPa
    end
end
% Hodógrafo
ax3 = axes('Position', [0.67 0.18 0.30 0.66]); hold(ax3, 'on');
cores = {[0.86 0.15 0.15], [0.06 0.62 0.35], [0.12 0.45 0.80], [0.55 0.30 0.85]};
faixas = [0 1000; 1000 3000; 3000 6000; 6000 12000];
nomes = {'0-1 km', '1-3 km', '3-6 km', '6-12 km'};
iw = find(temvento & h <= 12000);
hl = [];
for k = 1:4
    sel = iw(h(iw) >= faixas(k, 1) & h(iw) <= faixas(k, 2));
    if numel(sel) >= 2
        hl(end+1) = plot(ax3, u_kt(sel), v_kt(sel), '-', 'Color', cores{k}, 'LineWidth', 2.2); %#ok<AGROW>
    end
end
lim = max(20, 10 * ceil(max(abs([u_kt(iw); v_kt(iw)])) / 10));
th = linspace(0, 2 * pi, 200);
for r = 10:10:lim
    plot(ax3, r * cos(th), r * sin(th), ':', 'Color', [0.6 0.6 0.6]);
end
plot(ax3, [-lim lim], [0 0], 'Color', [0.5 0.5 0.5]); plot(ax3, [0 0], [-lim lim], 'Color', [0.5 0.5 0.5]);
leg = nomes(1:numel(hl));
if all(isfinite(F.bunkers_lm))
    hl(end+1) = plot(ax3, F.bunkers_lm(1) / 0.514444, F.bunkers_lm(2) / 0.514444, 's', 'MarkerSize', 10, ...
                     'MarkerFaceColor', [0.12 0.45 0.80], 'MarkerEdgeColor', 'k');
    hl(end+1) = plot(ax3, F.bunkers_rm(1) / 0.514444, F.bunkers_rm(2) / 0.514444, 'd', 'MarkerSize', 10, ...
                     'MarkerFaceColor', [0.86 0.15 0.15], 'MarkerEdgeColor', 'k');
    leg = [leg, {sprintf('Bunkers LM (%.0f kt)', norm(F.bunkers_lm) / 0.514444), ...
                 sprintf('Bunkers RM (%.0f kt)', norm(F.bunkers_rm) / 0.514444)}];
end
axis(ax3, 'equal'); axis(ax3, [-lim lim -lim lim]); box(ax3, 'on');
xlabel(ax3, 'u (nós)', 'FontWeight', 'bold'); ylabel(ax3, 'v (nós)', 'FontWeight', 'bold');
title(ax3, 'Hodógrafo e movimento de Bunkers');
legend(ax3, hl, leg, 'Location', 'southoutside', 'Orientation', 'horizontal');
print(fig1, fullfile(pasta, 'skewt_hodografo.png'), '-dpng', '-r130');

% ---------------- perfis de estabilidade ----------------
s = p >= p_topo;
ps = p(s); zs = z(s); Ts = T(s);
[theta, thetae] = thermo_td(Ts, ps, Td(s));           % K (thetae de Bolton, 1980)
[~, thetaes] = thermo_td(Ts, ps, Ts);                 % saturado: Td = T
g = 9.81;
N2 = g ./ theta .* gradient(theta, zs);               % frequência de Brunt-Väisälä ao quadrado (s^-2)
S = -((Ts + 273.15) ./ theta) .* gradient(theta, ps); % estabilidade estática (K/hPa)
F.p = ps; F.theta = theta; F.thetae = thetae; F.thetaes = thetaes; F.N2 = N2; F.S = S;

fig2 = figure('Name', ['Perfis - ' rotulo], 'Color', 'w', 'Position', [60 60 1350 600]);
tk = [1000 925 850 700 600 500 400 300 250 200];
tk = tk(tk >= p_topo);
subplot(1, 3, 1);
semilogy(theta, ps, 'b', thetae, ps, 'r', thetaes, ps, 'g--', 'LineWidth', 1.8);
legend('\theta', '\theta_e', '\theta_{es}', 'Location', 'northwest');
xlabel('Temperatura potencial (K)'); title('\theta, \theta_e e \theta_{es}');
subplot(1, 3, 2);
semilogy(N2 * 1e4, ps, 'k', 'LineWidth', 1.6); hold on; semilogy([0 0], [p_topo 1050], 'r--');
xlabel('N^2 (10^{-4} s^{-2})'); title('Brunt-Väisälä N^2');
subplot(1, 3, 3);
semilogy(S, ps, 'Color', [0.12 0.45 0.80], 'LineWidth', 1.6); hold on; semilogy([0 0], [p_topo 1050], 'r--');
xlabel('S = -(T/\theta) \partial\theta/\partialp (K/hPa)'); title('Estabilidade estática S');
for k = 1:3
    subplot(1, 3, k);
    set(gca, 'YDir', 'reverse', 'YTick', fliplr(tk), 'FontWeight', 'bold'); ylim([p_topo 1050]); grid on;
    if k == 1, ylabel('Pressão (hPa)'); end
end
if exist('sgtitle', 'file'), sgtitle(['Perfis de estabilidade - ' rotulo], 'FontWeight', 'bold'); end
print(fig2, fullfile(pasta, 'perfis_estabilidade.png'), '-dpng', '-r130');
end

function m = media_camada(p, h, u, v, hbase, htopo)
% Média do vento na camada [hbase, htopo] (m acima da superfície), ponderada pela pressão,
% com os limites interpolados em altura (como em MetPy.bunkers_storm_motion).
pb = interp1(h, log(p), hbase); pt = interp1(h, log(p), htopo);
sel = h > hbase & h < htopo;
pp = [exp(pb); p(sel); exp(pt)];
uu = [interp1(log(p), u, pb); u(sel); interp1(log(p), u, pt)];
vv = [interp1(log(p), v, pb); v(sel); interp1(log(p), v, pt)];
m = [trapz(pp, uu), trapz(pp, vv)] / (pp(end) - pp(1));
end
