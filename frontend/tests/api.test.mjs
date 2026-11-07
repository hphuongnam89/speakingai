import test from "node:test";
import assert from "node:assert/strict";
import {api,errorMessage,ApiError} from "../src/api.ts";

test("validation errors are readable and do not render server internals",()=>{
  assert.equal(errorMessage({detail:[{loc:["body","password"],input:"secret"}]}),"Kiểm tra lại các trường đã nhập.");
  assert.equal(errorMessage({detail:"Profile not found"}),"Profile not found");
});
test("API uses cookies and the selected profile, without an embedded API key",async()=>{
  const original=global.fetch;
  try{
    global.fetch=async(url,options)=>{assert.equal(url,"/api/v1/learning/units");assert.equal(options.credentials,"same-origin");assert.equal(options.headers.get("X-Profile-Id"),"my-profile");assert.equal(options.headers.get("X-API-Key"),null);return new Response(JSON.stringify({lessons:[]}));};
    assert.deepEqual(await api("/learning/units",{},"my-profile"),{lessons:[]});
  }finally{global.fetch=original;}
});
test("401 is distinguished from a transport failure",async()=>{
  const original=global.fetch;
  try{global.fetch=async()=>new Response(JSON.stringify({detail:"Expired"}),{status:401});await assert.rejects(api("/auth/session"),e=>e instanceof ApiError&&e.status===401);}
  finally{global.fetch=original;}
});
