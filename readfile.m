clear all;
close all;
clc;

addpath('YAMLMatlab')
%% select data file

filename = 'FUNcube-1_39444_201808311030';

viewMatplot = 1; % 1 to plot matlab figure for inspection
construct_bmp = 0; % 1 to construct BMP of selected waterfall plot

yml = ReadYaml([filename '.yml']);

%% cut wav file in to pieces

% particular settings for the pass
ftune = yml.Sat.State.TuningFrequency; % not needed in the creation of the figure
Fs = yml.Sat.Record.sample_rate;
Ttime = yml.Sat.Predict.LengthOfPass;
Dt = 0.1;

% time and length settings
L = Ttime.*Fs;
Lpart = round(L/(Ttime/Dt));

% Fourier transformation settings
NFFT = 2^nextpow2(Lpart);
%NFFT = 16384;
%NFFT = 8192;
%NFFT = 65536;
%NFFT = 32768;
half = NFFT/2;

%% get values for axis waterfall plot
f0 = 0;%ftune; % if absolute plot, then replace with center frequency
nx = Fs/NFFT;
ny = Dt;
bandwidth = f0-Fs/2+nx/2:nx:f0+Fs/2-nx/2;
time = 1:ny:Ttime;
Timeband = Ttime/Dt;

%%

%[Xchirp] = create_LORAchirp(-ftune,125e3,0.0165,-ftune,Fs,10,0.0145);

%% set certain zoom area
% lbound = 12000;    % Delfi-C3 zoom
% rbound = 24000;    % Delfi-C3 zoom

lbound = -124900;
rbound = 124900;

%lbound = -149900;
%rbound = 149900;

% lbound = -50000;
% rbound =  85000;

%lbound = -40000;   % FunCube-1
%rbound = -30000;    % FunCube-1

lfreq = min(find(bandwidth>lbound));
rfreq = min(find(bandwidth>rbound));

% time bounds

% ltbound = 424;
% rtbound = 434;

%ltbound = 1;
% %rtbound = length(time);

%ltime = min(find(time>ltbound));
%rtime = min(find(time>rtbound));
ltime = time(1);
rtime = length(time);%

Waterfall  = zeros(length(time(ltime:rtime)),length(bandwidth(lfreq:rfreq)));
%%
f = fopen ([filename '.32fc'], 'rb');
for i = 1:Ttime/Dt

    % read segment of the complete signal
    if (f < 0)
        %v = 0;
        error(['File: ' filename '.32fc not read!!!'])
    else
        t = fread (f, [2, Lpart], 'float');
        %fclose (f);
        v = t(1,:) - t(2,:)*1i;
        % v = (t(1,:) - t(2,:)*1i);
        [r, c] = size (v);
        v = reshape (v, c, r);
    end

    % complete segments, otherwise stop!
    if ~Lpart==length(v)
        break;
    end

    if i >= ltime && i < rtime
        % perform fast fourier transform on the segment and shift the spectrum

        bc = 1 + (i - ltime)*Lpart;
        ec = Lpart + (i - ltime)*Lpart;

        Y = fft(v,NFFT);
        Y = fftshift(Y);

        % only take the absolute values of the complex fourier transform
        line = abs(Y(1:NFFT))./Lpart;

        % place the line in the complete Waterfall matrix
        Waterfall(i+1-ltime,:) = line(lfreq:rfreq);
    end

    % display number segment and remove old data
    disp(i)
    %clear Y
end
fclose(f);

%% plot the zoomed-in waterfall plot in matlab for inspection
if viewMatplot==1
    load('spectrogramCMAP.mat')
    figure%('Visible','off')
    imagesc(bandwidth(lfreq:rfreq).*1e-3,time(ltime:rtime),10*log10(Waterfall))
    %imagesc(bandwidth(lfreq:rfreq).*1e-3+468500,time,10*log(Waterfall))
    caxis([-90 -50])
    c = colorbar;
    %cc = colormap;
    %colormap(C);
    ylabel('Time [sec]','FontSize',20)
    ylabel(c,'Energy [dB]','FontSize',20)
    xlabel(['Frequency offset to ' num2str(ftune./1e6) ' MHz [kHz]'],'FontSize',20)
    set(gca,'FontSize',20,'YDir','normal')
end

%% Write waterfall plot to BMP file.
if construct_bmp == 1
    imwrite(flipud((Waterfall).*300),cc ,[filename '.bmp'],'bmp')
end