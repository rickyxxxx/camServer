let currentPage = 0;
let images = [];
var curr_name = "";

function fetchAndDisplayImages() {
    fetch(`/images/${currentPage}`)
        .then(response => response.json())
        .then(data => {
            images = data.sort((a, b) => a[1].localeCompare(b[1])).reverse();
            displayImages(); // Ensure displayImages is called here
        })
        .catch(error => console.error('Error fetching images:', error));
}

function displayImages() {
    const galleryContent = document.getElementById('galleryContent');
    galleryContent.innerHTML = ''; // Clear previous images
    galleryContent.style.display = 'grid';
    galleryContent.style.gridTemplateColumns = 'repeat(4, 1fr)';
    galleryContent.style.gap = '10px';


    for (let i = 0; i < 4; i++) {
        const row = document.createElement('div');
        row.className = 'row';

        for (let j = 0; j < 2; j++) {
            let index = i * 2 + j;
            if (index >= images.length)
                continue;
            const imageDiv = document.createElement('div');
            let exp_str = '';
            if (images[index][2] < 1000){
                exp_str = images[index][2] + ' us';
            } else if (images[index][2] < 1000000){
                exp_str = (images[index][2] / 1000) + ' ms';
            } else {
                exp_str = (images[index][2] / 1000000) + ' s';
            }
            var fname = images[index][0];
            imageDiv.className = 'image';
            imageDiv.innerHTML = `
                <div>
                    <img src='/static/images/${images[index][0]}.jpg' onclick="toggleFullscreen(this)" alt="">
                    <div>
                        <h2 style="margin: 0;">${images[index][1]}</h2>
                        <div style="margin-top: auto;">
                            <p>Exposure: ${exp_str}</p>
                            <p>Gain: ${images[index][3]}</p>
                        </div>
                        <button onclick="download_fits('${fname}')">Download Fits</button>
                    </div>
                </div>
            `;
            row.appendChild(imageDiv);
        }
        galleryContent.appendChild(row);
    }
}

function download_fits(name){
	window.location.href = '/download_fits/' + name + '.fits';
}

function clearPagination() {
    const pagination = document.getElementById('pagination');
    while (pagination.firstChild) {
        pagination.removeChild(pagination.firstChild);
    }
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
    fetchAndDisplayImages();
    clearPagination();
    setupPagination();
}

function setupPagination() {
    const pagination = document.getElementById('pagination');
    pagination.innerHTML = '';

    fetch('/get_total_pages')
        .then(response => response.json())
        .then(data => {
            let totalPages = data.totalPages;

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
                    button.innerText = page;
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

        })
}

function isNumber(value) {
    const number = Number(value);
    return Number.isInteger(number) && number >= 0;
}

function toggleFullscreen(img) {
    if (!document.fullscreenElement) {
        img.requestFullscreen().catch(err => {
            alert(`Error attempting to enable full-screen mode: ${err.message} (${err.name})`);
        });
    } else {
        document.exitFullscreen().then(r => {});
    }
}


function main(){
    fetchAndDisplayImages();
    setupPagination();
}

const input = document.getElementById('calendar-input');

function formatDate(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
        weekday: 'long',
        month: 'short',
        day: 'numeric',
        year: 'numeric'
    });
}

function onFilterClicked(){

}

// Set default to today
const today = new Date().toISOString().split('T')[0];
input.value = today;
input.title = formatDate(today);

// Update the tooltip/hover display after date selection
input.addEventListener('change', () => {
    input.title = formatDate(input.value);
});

main();


