import {createPagination} from './utils/utils'
import {getFilters} from "../helpers/filters"
import {update} from '../helpers/helpers'
import wordCloud from '../graphs/word-cloud-modal'
import { metadataFiltersURL } from "../helpers/filters";
let content = document.getElementById("data-table-content");
export function createTable(page){
    update.startUpdate()
    content.innerHTML = "Loading...";
    let pagination = document.getElementById("data-table-pagination");
    pagination.innerHTML = ""
    let pageSize = document.getElementById("data-table-page-size").value
    let filtersValues = getFilters() 
    let urlParams = new URLSearchParams({
        "date-from": filtersValues.dateFrom,
        "date-to": filtersValues.dateTo,
        "languages": encodeURIComponent(filtersValues.languages),
        "sources": encodeURIComponent(filtersValues.sources),
        "sourcesID": filtersValues.sourcesID
    })+ "&" +  metadataFiltersURL()
    document.getElementById("data-items-table-csv").href = `/api/new-data/project/${window.project_id}/?format=csv&` + urlParams
    fetch(`/api/new-data/project/${window.project_id}/?page=${page}&page-size=${pageSize}&` + urlParams)
    .then((response) => response.json())
    .then((data) => {
        content.innerHTML = "";
        for (let element of data.data) {
            let tr = document.createElement("tr");
            var length = 150;
            let text = "";
            if(element.text.length > length){
                text = element.text.substring(0, length) + "...";
            } else {
                text = element.text
            }
            let row = `
        <td>
        <small>${element.dateCreated}</small>
       </td>
       <td>
         ${text}
       </td>
       <td >
        <b>${element.sourceLabel}</b>
       </td>
       <td class="text-center">
         ${element.sentimentValue.toFixed(4)}
       </td>
       <td class="text-center">
         <a href="#" class="info-button">${element.languageCode}</a>
       </td>
        `;
            tr.innerHTML = row;
            content.append(tr);
        }
        let firstElement = data.pageSize * (data.currentPage - 1) + 1;
        let lastElement = firstElement + data.pageSize - 1;
        createPagination(firstElement, lastElement, data.total, data.currentPage, data.totalPages, pagination, createTable);
        update.finishUpdate()
    });
}

document.querySelector("#show-word-cloud-data-items-table").addEventListener("click", (e)=>{
    document.querySelector("#word-cloud-modal").style.display = "block"
    let filtersValues = getFilters() 
    let urlParams = new URLSearchParams({
        "date-from": filtersValues.dateFrom,
        "date-to": filtersValues.dateTo,
        "languages": encodeURIComponent(filtersValues.languages),
        "sources": encodeURIComponent(filtersValues.sources),
        "sourcesID": filtersValues.sourcesID
    })
    let wordCloudURL = `/api/new-data/project/${window.project_id}/?format=word-cloud&` + urlParams
    wordCloud(wordCloudURL)
})
//createTable(1);
/*
<div class="col-12 col-md-auto">
        <ul class="pagination">
        <li>
            <a href="#">
            <i class="fe fe-chevron-left"></i>
            </a>
        </li>
        <li class="active">
            <a href="#">01</a>
        </li>
        <li>
            <a href="#">02</a>
        </li>
        <li>
            <a href="#">03</a>
        </li>
        <li>
            <a href="#">04</a>
        </li>
        <li>
            <a href="#">..</a>
        </li>
        <li>
            <a href="#">25</a>
        </li>
        <li>
            <a href="#"> <i class="fe fe-chevron-right"></i></a>
        </li>
        
        </ul>
    </div>
*/
