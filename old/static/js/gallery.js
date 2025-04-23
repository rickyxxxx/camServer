let currentPage = 0;
let images = [];
let colCount = 4;
let rowCount = 2;

function getImageList() {
    fetch('/search/None')
        .then(response => response.json())
        .then(data => {
            images = data;
            displayImages();
            displayPagination();
        })
        .catch(error => {
            console.error('Error fetching image list:', error);
        });
}

function getImageListCond(datetime) {
    fetch(`/search/${datetime}`)
        .then(response => response.json())
        .then(data => {
            images = data;
            displayImages();
            displayPagination();
        })
        .catch(error => {
            console.error('Error fetching image list:', error);
        });
}

function displayImages() {
    const galleryContent = document.getElementById('galleryContent');
    galleryContent.innerHTML = ''; // Clear previous images
    galleryContent.style.display = 'grid';
    galleryContent.style.gridTemplateColumns = 'repeat(4, 1fr)';
    galleryContent.style.gap = '10px';


    for (let i = 0; i < colCount; i++) {
        const row = document.createElement('div');
        row.className = 'row';

        for (let j = 0; j < rowCount; j++) {
            let index = i * rowCount + j + currentPage * rowCount * colCount;
            if (index >= images.length)
                continue;

            const imageDiv = document.createElement('div');

            const units = ['us', 'ms', 's']
            let expTime = parseInt(images[index]['ExpTime'])
            let ctr = 0;
            while (expTime >= 1000){
                expTime /= 1000;
                ++ctr;
            }
            let expStr = expTime.toFixed(2) + " " + units[ctr];
            // let expStr = `${expTime} ${units[ctr]}`

            let filepath = images[index]['ImgPath']

            imageDiv.className = 'image';
            imageDiv.innerHTML = `
                <h2 style="margin: 0;">${images[index]["CamName"]}</h2>
                <img src='/get_file/${filepath}.jpg' onclick="onImageClicked(this)" alt="">
                <div style="margin-top: auto;">
                    <p>Timestamp: ${images[index]['Datetime']}</p>
                    <p>Exposure: ${expStr}</p>
                    <p>Gain: ${images[index]['Gain']}</p>
                    <p>Bit Depth: ${images[index]['BitDepth']}</p>
                    <button onclick="onDownloadClicked('${filepath}')">Download</button>
                </div>
            `;
            row.appendChild(imageDiv);
        }
        galleryContent.appendChild(row);
    }
}

function onImageClicked(imageElement) {
    if (!document.fullscreenElement) {
        // Enter fullscreen mode
        if (imageElement.requestFullscreen) {
            imageElement.requestFullscreen();
        } else if (imageElement.webkitRequestFullscreen) { // Safari
            imageElement.webkitRequestFullscreen();
        } else if (imageElement.msRequestFullscreen) { // IE/Edge
            imageElement.msRequestFullscreen();
        }
    } else {
        // Exit fullscreen mode
        if (document.exitFullscreen) {
            document.exitFullscreen();
        } else if (document.webkitExitFullscreen) { // Safari
            document.webkitExitFullscreen();
        } else if (document.msExitFullscreen) { // IE/Edge
            document.msExitFullscreen();
        }
    }
}

function onDownloadClicked(name){
    // pop-up a window allowing the user to choose which file to download
    window.location.href = '/get_file/' + name + '.fits';
}

function clearPagination() {

}

function calcPagingLabel(totalPages) {
    let page_index = [1, 2];
    if (totalPages <= 1)
        return [1];
    if (totalPages <= 5){
        for (let i = 3; i <= totalPages; i++)
            page_index.push(i);
        return page_index;
    }

    // if the code reaches here, totalPages > 5
    let start_page = Math.max(currentPage - 1, 1);
    let end_page = Math.min(currentPage + 3, totalPages);
    if (start_page > 3)
        page_index.push(-1);
    start_page = Math.max(start_page, 3);
    for (let i = start_page; i <= end_page; i++){
        page_index.push(i);
    }
    if (end_page < totalPages - 2) {
        page_index.push(-1);
        for (let i = totalPages - 1; i <= totalPages; i++)
            page_index.push(i);
    } else {
        for (let i = end_page + 1; i <= totalPages; i++)
            page_index.push(i);
    }
    return page_index;
}

function updatePage(){
    displayImages();
    displayPagination();
}

function displayPagination() {
    const pagination = document.getElementById('pagination');

    // clear pagination if any
    while (pagination.firstChild) {
        pagination.removeChild(pagination.firstChild);
    }
    pagination.innerHTML = '';

    let gridSize = rowCount * colCount;
    let totalPages = Math.ceil(images.length / gridSize);

    const prev = document.createElement('button');
    prev.innerText = '<';
    prev.className = 'labelButton';
    prev.disabled = currentPage === 0;
    prev.onclick = () => {
        if (currentPage > 0) {
            currentPage--;
            updatePage();
        }
    }
    pagination.appendChild(prev);

    calcPagingLabel(totalPages).forEach(page => {
        const button = document.createElement('button');
        if (page === -1){
            button.innerText = '...';
            button.disabled = true;
            button.className='labelButton';
        } else {
            button.innerText = `${page}`;
            button.className = 'pageButton';
            button.disabled = page === currentPage + 1;
            button.onclick = () => {
                currentPage = page - 1;
                updatePage()
            }
        }
        pagination.appendChild(button);
    });

    const next = document.createElement('button');
    next.innerText = '>';
    next.className = 'labelButton';
    next.disabled = currentPage === totalPages - 1;
    next.onclick = () => {
        if (currentPage < totalPages - 1) {
            currentPage++;
            updatePage();
        }
    }
    pagination.appendChild(next);

    const index = document.createElement("p")
    index.innerText = `Page ${currentPage + 1} of ${Math.max(totalPages, 1)}`;
    pagination.appendChild(index);


    const goto_input = document.createElement('input');
    goto_input.id = 'gi';
    const goto = document.createElement('button');
    goto.innerText = 'Go to';
    goto.onclick = () => {
        gi = document.getElementById('gi');
        isNumber(gi.value) && gi.value > 0 && gi.value <= totalPages ? currentPage = gi.value - 1 : alert("Invalid page number");
        updatePage();
    }

    pagination.appendChild(goto_input);
    pagination.appendChild(goto);
}

function isNumber(value) {
    const number = Number(value);
    return Number.isInteger(number) && number >= 0;
}

function updateButtonText(selectElement, buttonId) {
    const selectedTag = selectElement.value; // Get the selected tag
    const button = document.getElementById(buttonId); // Get the button by ID
    button.textContent = `Selected: ${selectedTag}`; // Update button text
}

function onFilterClicked(){
    const calendarInput = document.getElementById("calendar-input"); // Get the input element
    const selectedDate = calendarInput.value; // Get the value of the input

    if (selectedDate === "") {
        getImageList();
    } else {
        let cond = `${selectedDate}T00:00:00,${selectedDate}T23:59:59`
        getImageListCond(cond);
    }
    currentPage = 0;
}

getImageList();