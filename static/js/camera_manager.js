function createCameraCard(cameraName, daytimeGain, daytimeExposure, daytimeInterval, nighttimeGain, nighttimeExposure, nighttimeInterval) {
    let cameraCard = document.createElement('div');
    cameraCard.classList.add('camera-card');

    let cameraTitle = document.createElement('h3');
    cameraTitle.textContent = cameraName;
    cameraCard.appendChild(cameraTitle);

    let settingsSection = document.createElement('div');
    settingsSection.classList.add('settings-section');

    let timeMode = document.createElement('div');
    timeMode.classList.add('time-mode');

    let daytimeSettings = document.createElement('div');
    let daytimeSettingsTitle = document.createElement('h4');
    daytimeSettingsTitle.textContent = 'Daytime Settings';
    daytimeSettings.appendChild(daytimeSettingsTitle);

    let daytimeGainLabel = document.createElement('label');
    daytimeGainLabel.textContent = 'Gain: ';
    let daytimeGainInput = document.createElement('input');
    daytimeGainInput.type = 'text';
    daytimeGainInput.placeholder = `Current: ${daytimeGain}`;
    daytimeGainLabel.appendChild(daytimeGainInput);
    daytimeSettings.appendChild(daytimeGainLabel);

    let daytimeExposureLabel = document.createElement('label');
    daytimeExposureLabel.textContent = 'Exposure: ';
    let daytimeExposureInput = document.createElement('input');
    daytimeExposureInput.type = 'text';
    daytimeExposureInput.placeholder = `Current: ${daytimeExposure}`;
    daytimeExposureLabel.appendChild(daytimeExposureInput);
    daytimeSettings.appendChild(daytimeExposureLabel);

    let daytimeIntervalLabel = document.createElement('label');
    daytimeIntervalLabel.textContent = 'Interval: ';
    let daytimeIntervalInput = document.createElement('input');
    daytimeIntervalInput.type = 'text';
    daytimeIntervalInput.placeholder = `Current: ${daytimeInterval}`;
    daytimeIntervalLabel.appendChild(daytimeIntervalInput);
    daytimeSettings.appendChild(daytimeIntervalLabel);

    timeMode.appendChild(daytimeSettings);

    let nighttimeSettings = document.createElement('div');
    let nighttimeSettingsTitle = document.createElement('h4');
    nighttimeSettingsTitle.textContent = 'Nighttime Settings';
    nighttimeSettings.appendChild(nighttimeSettingsTitle);

    let nighttimeGainLabel = document.createElement('label');
    nighttimeGainLabel.textContent = 'Gain: ';
    let nighttimeGainInput = document.createElement('input');
    nighttimeGainInput.type = 'text';
    nighttimeGainInput.placeholder = `Current: ${nighttimeGain}`;
    nighttimeGainLabel.appendChild(nighttimeGainInput);
}


