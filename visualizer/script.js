// Constants
const BASE_SLIDE_PATH = '../../output/dzi/';

// Helper Functions
function buildSlideName(cancerType, patient) {
    return cancerType + '_' + patient + '.dzi';
}

function buildAttentionSlideName(cancerType, patient, signature, model, epoch) {
    return cancerType + '_' + patient + '_' + signature.replaceAll(' ', '-').toUpperCase() + '_' + model + '_' + String(epoch).padStart(2, '0') + '.dzi';
}

function openSlide(slide, attentionSlide) {
    viewer.open(BASE_SLIDE_PATH + slide);
    viewer.addTiledImage({
        tileSource: BASE_SLIDE_PATH + attentionSlide,
        opacity: opacity,
        success: function (event) {
            tiledImage = event.item;
        }
    });
}


// Patients for cancer type
var patients;
fetch('patients.json')
    .then(response => {
        if (!response.ok) {
            throw new Error('Not ok');
        }
        return response.json();
    })
    .then(data => {
        patients = data;
    })
    .catch(error => {
        console.error('There was a problem with the fetch operation:', error);
    });

var currentCancerType = 'TCGA-BRCA';
var currentPatient = 'TCGA-A2-A0EY';
var currentSignature = 'Tumor Suppressor Genes'
var currentEpoch = 20
var currentModel = 'NaCAGaT';

var cancerSelector = document.getElementById('cancerSelector');
var patientSelector = document.getElementById('patientSelector');
var signatureSelector = document.getElementById('signatureSelector');
var epochSelector = document.getElementById('epochSelector');
var modelSelector = document.getElementById('modelSelector');
var notesDiv = document.getElementById('notes');

var currentSlideName = buildSlideName(currentCancerType, currentPatient);
var currentAttentionSlideName = buildAttentionSlideName(currentCancerType, currentPatient, currentSignature, currentModel, currentEpoch);

// Cancer Type Selector
cancerSelector.addEventListener('change', function () {
    currentCancerType = cancerSelector.value;
    var i, L = patientSelector.options.length - 1;
    for (i = L; i >= 0; i--) {
        patientSelector.remove(i);
    }
    var cancerTypePatients = patients[currentCancerType];
    cancerTypePatients.forEach(patient => {
        if (patient['visible'] == true) {
            var opt = document.createElement('option');
            opt.value = patient['id'];
            opt.textContent = patient['id'];
            patientSelector.appendChild(opt);
        }
    });

    patientSelector.dispatchEvent(new Event('change'));
});

// Patient Selector
patientSelector.addEventListener('change', function () {
    currentPatient = patientSelector.value;
    var i, L = signatureSelector.options.length - 1;
    for (i = L; i >= 0; i--) {
        signatureSelector.remove(i);
    }
    L = epochSelector.options.length - 1;
    for (i = L; i >= 0; i--) {
        epochSelector.remove(i);
    }
    var signatures = patients[currentCancerType].filter(function (patient) {
        return patient['id'] == currentPatient;
    })[0]['signatures'];
    signatures.forEach(signature => {
        var opt = document.createElement('option');
        opt.value = signature['name'];
        opt.textContent = signature['name'];
        signatureSelector.appendChild(opt);
    });

    notesDiv.innerHTML = '';

    var notes = patients[currentCancerType].filter(function (patient) {
        return patient['id'] == currentPatient;
    })[0]['notes'];
    if (notes != null) {
        var p = document.createElement('p');
        p.textContent = 'Notes: ' + notes;
        notesDiv.appendChild(p);
    }

    signatureSelector.dispatchEvent(new Event('change'));
    epochSelector.dispatchEvent(new Event('change'));
});

// Signature Selector
signatureSelector.addEventListener('change', function () {
    currentSignature = signatureSelector.value;
    var i, L = epochSelector.options.length - 1;
    for (i = L; i >= 0; i--) {
        epochSelector.remove(i);
    }
    var signatures = patients[currentCancerType].filter(function (patient) {
        return patient['id'] == currentPatient;
    })[0]['signatures'];
    var epochs = signatures.filter(function (signature) {
        return signature['name'] == currentSignature;
    })[0]['epochs'];
    epochs.forEach(epoch => {
        var opt = document.createElement('option');
        opt.value = epoch;
        opt.textContent = 'Epoch ' + epoch;
        epochSelector.appendChild(opt);
    });

    epochSelector.dispatchEvent(new Event('change'));
});

// Epoch Selector
epochSelector.addEventListener('change', function () {
    currentEpoch = epochSelector.value;

    currentSlideName = buildSlideName(currentCancerType, currentPatient);
    currentAttentionSlideName = buildAttentionSlideName(currentCancerType, currentPatient, currentSignature, currentModel, currentEpoch);
    console.log(currentAttentionSlideName);
    openSlide(currentSlideName, currentAttentionSlideName);
});

// Model Selector
modelSelector.addEventListener('change', function () {
    currentModel = modelSelector.value;

    currentSlideName = buildSlideName(currentCancerType, currentPatient);
    currentAttentionSlideName = buildAttentionSlideName(currentCancerType, currentPatient, currentSignature, currentModel, currentEpoch);
    console.log(currentAttentionSlideName);
    openSlide(currentSlideName, currentAttentionSlideName);
});

var viewer = OpenSeadragon({
    id: "slide",
    prefixUrl: "openseadragon/images/",
    tileSources: BASE_SLIDE_PATH + currentSlideName,
    showNavigator: true,
});

var tiledImage;
var opacity = 0.0;
viewer.addTiledImage({
    tileSource: BASE_SLIDE_PATH + currentAttentionSlideName,
    opacity: opacity,
    success: function (event) {
        tiledImage = event.item;
    }
});

document.getElementById('toggleButton').addEventListener('click', function () {
    if (tiledImage) {
        if (opacity > 0.0) {
            opacity = 0.0;
            tiledImage.setOpacity(opacity);
            document.getElementById('indicator').style.display = 'none';
        } else {
            opacity = 0.5;
            tiledImage.setOpacity(opacity);
            document.getElementById('indicator').style.display = 'block';
        }
    }
});
