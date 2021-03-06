import {createPagination} from './utils/utils'
import {createTable as dataModalTable} from './data_table_modal.jsx'
import {update, manageTableOrderFilters} from '../helpers/helpers'
import wordCloud from '../graphs/word-cloud-modal'
import { metadataFiltersURL , normalFiltersURL, orderFilters} from "../helpers/filters";
import reactDom from 'react-dom'
import React from 'react'
import Pagination from '../../components/Pagination'
export function createTable(pageNumber){
    update.startUpdate()
    makeTable(pageNumber)
}

let pageSizeDropdown = document.querySelector("#aspect-topic-table-page-size")
let content = document.getElementById("aspect-topic-table-content");
let table = document.querySelector("[data-graph-table='aspect-topic']")
let orderElements = table.querySelectorAll("[data-order-by]")
manageTableOrderFilters(table, createTable)

function makeTable(page){
    content.innerHTML = "Loading...";
    
	let pagination = document.getElementById("aspect-topic-table-pagination");
    pagination.innerHTML = ""

    let pageSize = pageSizeDropdown.value
    let urlParams = metadataFiltersURL() + "&" + normalFiltersURL()

    document.getElementById("aspect-topic-table-csv").href= `/api/aspect-topic/project/${window.project_id}/?format=csv&` + urlParams
    fetch(`/api/aspect-topic/project/${window.project_id}/?page=${page}&page_size=${pageSize}&` + urlParams + "&" + orderFilters(table))
    .then((response) => response.json())
    .then((data) => {
        content.innerHTML = ""
        for (let element of data.data) {
            let tr = document.createElement("tr");
            let row = `
            <td>${element.topicLabel}</td>
            <td>${element.aspectLabel}</td>
            <td class="text-center">
            <a style="cursor:pointer" class="info-button green" data-aspect="${element.aspectLabel}" data-topic="${element.topicLabel}" data-sentiment="positive">${element.positivesCount}</a>
           </td>
           <td class="text-center">
            <a style="cursor:pointer" class="info-button red" data-aspect="${element.aspectLabel}" data-topic="${element.topicLabel}" data-sentiment="negative">${element.negativesCount}</a>
           </td>
            `;
                tr.innerHTML = row;
                content.append(tr);

		}
            
		let buttons =content.querySelectorAll("a[data-topic]")
		for(let button of buttons){
			button.addEventListener("click", (e)=>{
				let dataAspectLabel = e.target.getAttribute("data-aspect")
				let dataTopicLabel = e.target.getAttribute("data-topic")
				let sentiment = e.target.getAttribute("data-sentiment")
				document.querySelector("#data-table-modal").style.display = "block"
				let wordCloudURL = `/api/data-per-aspect-topic/${window.project_id}/?format=word-cloud&` + new URLSearchParams({
					"aspect-label": encodeURIComponent(dataAspectLabel),
					"topic-label": encodeURIComponent(dataTopicLabel),
					"sentiment": sentiment,
				})+ "&" +  metadataFiltersURL()+ "&" + normalFiltersURL()
				let options = {}
				options.csvURL = `/api/data-per-aspect-topic/${window.project_id}/?format=csv&` + new URLSearchParams({
					"aspect-label": encodeURIComponent(dataAspectLabel),
					"topic-label": encodeURIComponent(dataTopicLabel),
					"sentiment": sentiment,
				})+ "&" +  metadataFiltersURL()+ "&" + normalFiltersURL()
				options.dataURL = `/api/data-per-aspect-topic/${window.project_id}/?` + new URLSearchParams({
					"aspect-label": encodeURIComponent(dataAspectLabel),
					"topic-label": encodeURIComponent(dataTopicLabel),
					"sentiment": sentiment,
				})+ "&" +  metadataFiltersURL()+ "&" + normalFiltersURL()
				wordCloud(wordCloudURL)
				dataModalTable(1, options)
			})
		}
		let firstElement = data.pageSize * (data.currentPage - 1) + 1;
		let lastElement = firstElement + data.pageSize - 1;
		reactDom.render(
			<Pagination
				firstElement={firstElement}
				lastElement={lastElement}
				totalElements={ data.total}
				totalPages={data.totalPages}
				currentPageNumber={data.currentPage}
				callBack={createTable}
				options={options}
				divElement={pagination}
			/>,
			pagination
		)
		//createPagination(firstElement, lastElement, data.total, data.currentPage, data.totalPages, pagination, createTable);
		update.finishUpdate()
    });
}

pageSizeDropdown.addEventListener("change", ()=>{
    createTable(1)
})
