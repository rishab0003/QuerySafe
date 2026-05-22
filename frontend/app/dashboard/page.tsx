import React from 'react'
import DBConnector from '../../components/dashboard/DBConnector'
import ResultTable from '../../components/dashboard/ResultTable'
import ChatPanel from './ChatPanel'

export default function Dashboard(){
  return (
    <div className="flex gap-6">
      <aside className="w-72">
        <DBConnector />
      </aside>
      <section className="flex-1">
        <h2 className="text-xl font-semibold mb-4">Chat / Query</h2>
        <ChatPanel />
        <div className="mt-6">
          <ResultTable columns={["id","name","email"]} rows={[{id:1,name:'Alice',email:'a@example.com'}]} />
        </div>
      </section>
    </div>
  )
}
